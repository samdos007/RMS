"""Price snapshot model for P&L tracking."""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Numeric, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.idea import Idea


class PriceSource(str, Enum):
    """Source of price data."""
    YFINANCE = "YFINANCE"
    MANUAL = "MANUAL"


class PriceSnapshot(Base):
    """
    Price snapshot for tracking P&L over time.

    Stores both primary and secondary prices for pair trades.
    """

    __tablename__ = "price_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "idea_id",
            "timestamp",
            name="uq_idea_timestamp",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    idea_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )
    price_primary: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=False,
    )
    price_secondary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )
    source: Mapped[PriceSource] = mapped_column(
        String(20),
        nullable=False,
        default=PriceSource.MANUAL,
    )
    note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationship
    idea: Mapped["Idea"] = relationship(
        "Idea",
        back_populates="price_snapshots",
    )
