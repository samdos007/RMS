"""P&L calculation schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel

from app.models.idea import TradeType


class PnLResponse(BaseModel):
    """Schema for P&L calculation response."""

    idea_id: str
    trade_type: TradeType
    is_realized: bool

    # Entry prices
    entry_price_primary: Decimal
    entry_price_secondary: Optional[Decimal] = None

    # Current/Exit prices
    current_price_primary: Decimal
    current_price_secondary: Optional[Decimal] = None

    # P&L calculations
    pnl_percent: Decimal
    pnl_absolute: Optional[Decimal] = None

    # For pair trades, also show individual leg performance
    pnl_primary_leg: Optional[Decimal] = None  # Log return of primary leg
    pnl_secondary_leg: Optional[Decimal] = None  # Log return of secondary leg
    simple_spread: Optional[Decimal] = None  # Simple (non-log) spread return

    # Timestamp of price data
    price_timestamp: Optional[datetime] = None


class PnLHistoryPoint(BaseModel):
    """Schema for a single point in P&L history."""

    timestamp: datetime
    price_primary: Decimal
    price_secondary: Optional[Decimal] = None
    pnl_percent: Decimal
    pnl_primary_leg: Optional[Decimal] = None
    pnl_secondary_leg: Optional[Decimal] = None


class PnLHistoryResponse(BaseModel):
    """Schema for P&L history response."""

    idea_id: str
    trade_type: TradeType
    entry_price_primary: Decimal
    entry_price_secondary: Optional[Decimal] = None
    history: List[PnLHistoryPoint]
