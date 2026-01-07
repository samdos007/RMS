"""P&L calculation service."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from math import log
from typing import Optional, List

from app.models.idea import Idea, TradeType, PairOrientation
from app.models.price_snapshot import PriceSnapshot
from app.schemas.pnl import PnLResponse, PnLHistoryResponse, PnLHistoryPoint


@dataclass
class PnLResult:
    """Internal P&L calculation result."""

    pnl_percent: Decimal
    pnl_absolute: Optional[Decimal]
    pnl_primary_leg: Optional[Decimal]
    pnl_secondary_leg: Optional[Decimal]
    simple_spread: Optional[Decimal]


class PnLService:
    """
    P&L calculation service.

    Formulas:
    ---------
    LONG single:   (current - entry) / entry
    SHORT single:  (entry - current) / entry
    PAIR (log):    ln(P_long/P_long0) - ln(P_short/P_short0)
    """

    @staticmethod
    def calculate_long_pnl(entry_price: Decimal, current_price: Decimal) -> Decimal:
        """
        Calculate LONG single position P&L.

        Formula: (current - entry) / entry

        Example:
            Entry: $100, Current: $110
            P&L = (110 - 100) / 100 = 0.10 = +10%
        """
        if entry_price <= 0:
            raise ValueError("Entry price must be positive")
        return (current_price - entry_price) / entry_price

    @staticmethod
    def calculate_short_pnl(entry_price: Decimal, current_price: Decimal) -> Decimal:
        """
        Calculate SHORT single position P&L.

        Formula: (entry - current) / entry

        Example:
            Entry: $100, Current: $90
            P&L = (100 - 90) / 100 = 0.10 = +10% (profit from decline)
        """
        if entry_price <= 0:
            raise ValueError("Entry price must be positive")
        return (entry_price - current_price) / entry_price

    @staticmethod
    def calculate_log_return(entry_price: Decimal, current_price: Decimal) -> Decimal:
        """Calculate log return for a single position."""
        if entry_price <= 0 or current_price <= 0:
            raise ValueError("Prices must be positive")
        return Decimal(str(log(float(current_price) / float(entry_price))))

    @staticmethod
    def calculate_pair_pnl_log(
        entry_price_long: Decimal,
        current_price_long: Decimal,
        entry_price_short: Decimal,
        current_price_short: Decimal,
    ) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        """
        Calculate PAIR trade P&L using log spread.

        Formula: ln(P_long/P_long0) - ln(P_short/P_short0)

        Returns: (spread_pnl, long_leg_return, short_leg_return, simple_spread)

        The spread P&L is positive when:
        - Long leg outperforms (goes up more or down less)
        - Short leg underperforms (goes down more or up less)

        Example:
            Long leg:  Entry $100, Current $110 -> ln(110/100) = 0.0953
            Short leg: Entry $50,  Current $48  -> ln(48/50)  = -0.0408

            Pair P&L = 0.0953 - (-0.0408) = 0.1361 = +13.61%
        """
        if (
            entry_price_long <= 0
            or entry_price_short <= 0
            or current_price_long <= 0
            or current_price_short <= 0
        ):
            raise ValueError("All prices must be positive")

        # Calculate log returns for each leg
        log_return_long = Decimal(
            str(log(float(current_price_long) / float(entry_price_long)))
        )
        log_return_short = Decimal(
            str(log(float(current_price_short) / float(entry_price_short)))
        )

        # Pair P&L: long leg return minus short leg return
        # We want LONG to go up and SHORT to go down
        spread_pnl = log_return_long - log_return_short

        # Simple spread for secondary display
        # (P_long/P_long0) / (P_short/P_short0) - 1
        ratio_long = current_price_long / entry_price_long
        ratio_short = current_price_short / entry_price_short
        simple_spread = ratio_long / ratio_short - 1

        return spread_pnl, log_return_long, log_return_short, simple_spread

    def calculate_idea_pnl(
        self,
        idea: Idea,
        current_price_primary: Decimal,
        current_price_secondary: Optional[Decimal] = None,
    ) -> PnLResult:
        """
        Calculate P&L for an idea based on its trade type.

        Args:
            idea: The Idea model
            current_price_primary: Current price of primary ticker
            current_price_secondary: Current price of secondary ticker (for pairs)

        Returns:
            PnLResult with calculated P&L values
        """
        if idea.trade_type == TradeType.LONG:
            pnl_pct = self.calculate_long_pnl(
                idea.entry_price_primary,
                current_price_primary,
            )
            pnl_abs = pnl_pct * idea.position_size if idea.position_size else None

            return PnLResult(
                pnl_percent=pnl_pct,
                pnl_absolute=pnl_abs,
                pnl_primary_leg=None,
                pnl_secondary_leg=None,
                simple_spread=None,
            )

        elif idea.trade_type == TradeType.SHORT:
            pnl_pct = self.calculate_short_pnl(
                idea.entry_price_primary,
                current_price_primary,
            )
            pnl_abs = pnl_pct * idea.position_size if idea.position_size else None

            return PnLResult(
                pnl_percent=pnl_pct,
                pnl_absolute=pnl_abs,
                pnl_primary_leg=None,
                pnl_secondary_leg=None,
                simple_spread=None,
            )

        elif idea.trade_type == TradeType.PAIR_LONG_SHORT:
            if not idea.entry_price_secondary or not current_price_secondary:
                raise ValueError("Secondary prices required for pair trade P&L")

            # Determine which leg is long based on pair orientation
            if idea.pair_orientation == PairOrientation.LONG_PRIMARY_SHORT_SECONDARY:
                entry_long = idea.entry_price_primary
                current_long = current_price_primary
                entry_short = idea.entry_price_secondary
                current_short = current_price_secondary
            else:  # SHORT_PRIMARY_LONG_SECONDARY
                entry_long = idea.entry_price_secondary
                current_long = current_price_secondary
                entry_short = idea.entry_price_primary
                current_short = current_price_primary

            spread_pnl, log_long, log_short, simple_spread = self.calculate_pair_pnl_log(
                entry_long,
                current_long,
                entry_short,
                current_short,
            )

            # For absolute P&L, use average position size (simplified)
            pnl_abs = None
            if idea.position_size:
                pnl_abs = spread_pnl * idea.position_size

            return PnLResult(
                pnl_percent=spread_pnl,
                pnl_absolute=pnl_abs,
                pnl_primary_leg=log_long
                if idea.pair_orientation == PairOrientation.LONG_PRIMARY_SHORT_SECONDARY
                else log_short,
                pnl_secondary_leg=log_short
                if idea.pair_orientation == PairOrientation.LONG_PRIMARY_SHORT_SECONDARY
                else log_long,
                simple_spread=simple_spread,
            )

        else:
            raise ValueError(f"Unknown trade type: {idea.trade_type}")

    def get_pnl_response(
        self,
        idea: Idea,
        current_price_primary: Decimal,
        current_price_secondary: Optional[Decimal] = None,
        price_timestamp: Optional[datetime] = None,
    ) -> PnLResponse:
        """
        Get a full P&L response for an idea.
        """
        # Use exit prices if closed
        if idea.is_closed and idea.exit_price_primary:
            current_price_primary = idea.exit_price_primary
            if idea.exit_price_secondary:
                current_price_secondary = idea.exit_price_secondary

        result = self.calculate_idea_pnl(
            idea,
            current_price_primary,
            current_price_secondary,
        )

        return PnLResponse(
            idea_id=idea.id,
            trade_type=idea.trade_type,
            is_realized=idea.is_closed,
            entry_price_primary=idea.entry_price_primary,
            entry_price_secondary=idea.entry_price_secondary,
            current_price_primary=current_price_primary,
            current_price_secondary=current_price_secondary,
            pnl_percent=result.pnl_percent,
            pnl_absolute=result.pnl_absolute,
            pnl_primary_leg=result.pnl_primary_leg,
            pnl_secondary_leg=result.pnl_secondary_leg,
            simple_spread=result.simple_spread,
            price_timestamp=price_timestamp,
        )

    def get_pnl_history(
        self,
        idea: Idea,
        snapshots: List[PriceSnapshot],
    ) -> PnLHistoryResponse:
        """
        Calculate P&L history from price snapshots.
        """
        history: List[PnLHistoryPoint] = []

        for snapshot in sorted(snapshots, key=lambda s: s.timestamp):
            try:
                result = self.calculate_idea_pnl(
                    idea,
                    snapshot.price_primary,
                    snapshot.price_secondary,
                )
                history.append(
                    PnLHistoryPoint(
                        timestamp=snapshot.timestamp,
                        price_primary=snapshot.price_primary,
                        price_secondary=snapshot.price_secondary,
                        pnl_percent=result.pnl_percent,
                        pnl_primary_leg=result.pnl_primary_leg,
                        pnl_secondary_leg=result.pnl_secondary_leg,
                    )
                )
            except ValueError:
                # Skip snapshots with invalid data
                continue

        return PnLHistoryResponse(
            idea_id=idea.id,
            trade_type=idea.trade_type,
            entry_price_primary=idea.entry_price_primary,
            entry_price_secondary=idea.entry_price_secondary,
            history=history,
        )
