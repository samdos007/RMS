"""Price service for yfinance integration."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, List, Tuple

import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from app.models.idea import Idea
from app.models.price_snapshot import PriceSnapshot, PriceSource


class PriceService:
    """
    Price service for fetching and storing price data from yfinance.

    Provides idempotent backfill functionality to avoid duplicate snapshots.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_current_price(self, ticker: str) -> Optional[Decimal]:
        """
        Fetch the current/latest price for a ticker.

        Returns None if the ticker is invalid or data is unavailable.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if hist.empty:
                return None
            return Decimal(str(round(hist["Close"].iloc[-1], 6)))
        except Exception:
            return None

    def get_current_prices(self, tickers: List[str]) -> Dict[str, Optional[Decimal]]:
        """
        Batch fetch current prices for multiple tickers.

        More efficient than calling get_current_price multiple times.
        """
        if not tickers:
            return {}

        result = {t: None for t in tickers}

        try:
            if len(tickers) == 1:
                result[tickers[0]] = self.get_current_price(tickers[0])
                return result

            # Batch download for multiple tickers
            data = yf.download(
                tickers=tickers,
                period="1d",
                progress=False,
                threads=True,
            )

            if data.empty:
                return result

            for ticker in tickers:
                try:
                    if len(tickers) == 1:
                        price = data["Close"].iloc[-1]
                    else:
                        price = data["Close"][ticker].iloc[-1]

                    if pd.notna(price):
                        result[ticker] = Decimal(str(round(price, 6)))
                except (KeyError, IndexError):
                    continue

        except Exception:
            pass

        return result

    def fetch_historical_prices(
        self,
        ticker: str,
        start_date: date,
        end_date: Optional[date] = None,
    ) -> List[Tuple[date, Decimal]]:
        """
        Fetch historical daily close prices for a ticker.

        Returns list of (date, price) tuples.
        """
        if end_date is None:
            end_date = date.today()

        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(
                start=start_date.isoformat(),
                end=(end_date + timedelta(days=1)).isoformat(),  # yfinance end is exclusive
            )

            if hist.empty:
                return []

            results = []
            for idx, row in hist.iterrows():
                snapshot_date = idx.date() if hasattr(idx, "date") else idx
                price = Decimal(str(round(row["Close"], 6)))
                results.append((snapshot_date, price))

            return results

        except Exception:
            return []

    def get_existing_snapshot_dates(
        self,
        idea_id: str,
    ) -> set[date]:
        """Get all dates that already have snapshots for an idea."""
        results = (
            self.db.query(PriceSnapshot.timestamp)
            .filter(PriceSnapshot.idea_id == idea_id)
            .all()
        )
        return {r[0].date() if isinstance(r[0], datetime) else r[0] for r in results}

    def backfill_prices_idempotent(
        self,
        idea: Idea,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        """
        Idempotent price backfill - only inserts snapshots for missing dates.

        This is safe to call multiple times; it will not create duplicate snapshots.

        Args:
            idea: The Idea to backfill prices for
            start_date: Start date (defaults to idea.start_date)
            end_date: End date (defaults to today)

        Returns:
            Number of new snapshots created
        """
        if start_date is None:
            start_date = idea.start_date
        if end_date is None:
            end_date = date.today()

        # Get existing snapshot dates
        existing_dates = self.get_existing_snapshot_dates(idea.id)

        # Fetch historical prices for primary ticker
        primary_prices = self.fetch_historical_prices(
            idea.folder.ticker_primary,
            start_date,
            end_date,
        )

        if not primary_prices:
            return 0

        # For pair trades, also fetch secondary prices
        secondary_prices_map: Dict[date, Decimal] = {}
        if idea.is_pair and idea.folder.ticker_secondary:
            secondary_prices = self.fetch_historical_prices(
                idea.folder.ticker_secondary,
                start_date,
                end_date,
            )
            secondary_prices_map = {d: p for d, p in secondary_prices}

        # Create snapshots for missing dates
        now = datetime.utcnow()
        created_count = 0

        for snapshot_date, price_primary in primary_prices:
            # Skip if we already have a snapshot for this date
            if snapshot_date in existing_dates:
                continue

            # For pair trades, skip if we don't have secondary price
            price_secondary = None
            if idea.is_pair:
                price_secondary = secondary_prices_map.get(snapshot_date)
                if price_secondary is None:
                    continue

            # Create snapshot with timestamp at end of trading day
            timestamp = datetime.combine(
                snapshot_date,
                datetime.max.time().replace(microsecond=0),
            )

            snapshot = PriceSnapshot(
                idea_id=idea.id,
                timestamp=timestamp,
                price_primary=price_primary,
                price_secondary=price_secondary,
                source=PriceSource.YFINANCE,
            )

            self.db.add(snapshot)
            created_count += 1

        if created_count > 0:
            self.db.commit()

        return created_count

    def fetch_latest_and_create_snapshot(
        self,
        idea: Idea,
    ) -> Optional[PriceSnapshot]:
        """
        Fetch the latest prices and create a snapshot.

        Returns the created snapshot or None if prices couldn't be fetched.
        """
        tickers = [idea.folder.ticker_primary]
        if idea.is_pair and idea.folder.ticker_secondary:
            tickers.append(idea.folder.ticker_secondary)

        prices = self.get_current_prices(tickers)

        price_primary = prices.get(idea.folder.ticker_primary)
        if price_primary is None:
            return None

        price_secondary = None
        if idea.is_pair:
            price_secondary = prices.get(idea.folder.ticker_secondary)
            if price_secondary is None:
                return None

        # Check if we already have a snapshot for today
        today = date.today()
        existing = (
            self.db.query(PriceSnapshot)
            .filter(
                PriceSnapshot.idea_id == idea.id,
                PriceSnapshot.timestamp >= datetime.combine(today, datetime.min.time()),
                PriceSnapshot.timestamp < datetime.combine(today + timedelta(days=1), datetime.min.time()),
            )
            .first()
        )

        if existing:
            # Update existing snapshot
            existing.price_primary = price_primary
            existing.price_secondary = price_secondary
            existing.source = PriceSource.YFINANCE
            self.db.commit()
            return existing

        # Create new snapshot
        snapshot = PriceSnapshot(
            idea_id=idea.id,
            timestamp=datetime.utcnow(),
            price_primary=price_primary,
            price_secondary=price_secondary,
            source=PriceSource.YFINANCE,
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        return snapshot

    def add_manual_snapshot(
        self,
        idea: Idea,
        timestamp: datetime,
        price_primary: Decimal,
        price_secondary: Optional[Decimal] = None,
        note: Optional[str] = None,
    ) -> PriceSnapshot:
        """
        Add a manual price snapshot.
        """
        # Validate pair trade has secondary price
        if idea.is_pair and price_secondary is None:
            raise ValueError("Secondary price required for pair trade")

        snapshot = PriceSnapshot(
            idea_id=idea.id,
            timestamp=timestamp,
            price_primary=price_primary,
            price_secondary=price_secondary,
            source=PriceSource.MANUAL,
            note=note,
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        return snapshot

    def get_price_on_date(self, ticker: str, target_date: date) -> Optional[Decimal]:
        """
        Get the closing price for a ticker on a specific date.

        Returns None if no data available for that date.
        """
        try:
            stock = yf.Ticker(ticker)
            # Fetch a small window around the target date
            start = target_date - timedelta(days=5)
            end = target_date + timedelta(days=2)

            hist = stock.history(
                start=start.isoformat(),
                end=end.isoformat(),
            )

            if hist.empty:
                return None

            # Try to find the exact date first
            for idx, row in hist.iterrows():
                snapshot_date = idx.date() if hasattr(idx, "date") else idx
                if snapshot_date == target_date:
                    return Decimal(str(round(row["Close"], 6)))

            # If exact date not found, return None (market was closed)
            return None

        except Exception:
            return None

    def get_theme_ticker_performance(
        self,
        tickers: List[str],
        theme_date: date,
    ) -> List[Dict]:
        """
        Get performance data for theme tickers since theme date.

        Returns list of dicts with ticker, start_price, current_price, pnl_percent.
        """
        results = []

        # Get current prices for all tickers
        current_prices = self.get_current_prices(tickers)

        # Get historical price on theme date for each ticker
        for ticker in tickers:
            start_price = self.get_price_on_date(ticker, theme_date)
            current_price = current_prices.get(ticker)

            pnl_percent = None
            if start_price and current_price:
                pnl_percent = float((current_price - start_price) / start_price * 100)

            results.append({
                "ticker": ticker,
                "start_price": float(start_price) if start_price else None,
                "current_price": float(current_price) if current_price else None,
                "pnl_percent": pnl_percent,
            })

        return results
