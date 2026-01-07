"""Earnings model for tracking estimates vs actuals."""

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Date, Numeric, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.folder import Folder


class PeriodType(str, Enum):
    """Type of reporting period."""
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"


class Earnings(Base, TimestampMixin):
    """
    Earnings data for a ticker.

    Tracks consensus estimate, user's estimate, and actual for EPS, revenue, EBITDA, and FCF.
    """

    __tablename__ = "earnings"
    __table_args__ = (
        UniqueConstraint(
            "folder_id",
            "ticker",
            "fiscal_quarter",
            name="uq_folder_ticker_quarter",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    folder_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ticker: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    # Period information
    period_type: Mapped[PeriodType] = mapped_column(
        String(20),
        nullable=False,
        default=PeriodType.QUARTERLY,
    )
    period: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    fiscal_quarter: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    period_end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    # EPS - Consensus estimate
    estimate_eps: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )
    actual_eps: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )
    my_estimate_eps: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )

    # Revenue (stored in raw dollars)
    estimate_rev: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=True,
    )
    actual_rev: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=True,
    )
    my_estimate_rev: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=True,
    )

    # EBITDA (stored in raw dollars)
    estimate_ebitda: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=True,
    )
    actual_ebitda: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=True,
    )
    my_estimate_ebitda: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=True,
    )

    # Free Cash Flow (stored in raw dollars)
    estimate_fcf: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=True,
    )
    actual_fcf: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=True,
    )
    my_estimate_fcf: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=True,
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationship
    folder: Mapped["Folder"] = relationship(
        "Folder",
        back_populates="earnings",
    )

    @property
    def eps_surprise(self) -> Optional[Decimal]:
        """Calculate EPS surprise (actual - estimate)."""
        if self.actual_eps is not None and self.estimate_eps is not None:
            return self.actual_eps - self.estimate_eps
        return None

    @property
    def eps_surprise_pct(self) -> Optional[Decimal]:
        """Calculate EPS surprise percentage."""
        if (
            self.actual_eps is not None
            and self.estimate_eps is not None
            and self.estimate_eps != 0
        ):
            return (self.actual_eps - self.estimate_eps) / abs(self.estimate_eps) * 100
        return None

    @property
    def rev_surprise(self) -> Optional[Decimal]:
        """Calculate revenue surprise (actual - estimate)."""
        if self.actual_rev is not None and self.estimate_rev is not None:
            return self.actual_rev - self.estimate_rev
        return None

    @property
    def rev_surprise_pct(self) -> Optional[Decimal]:
        """Calculate revenue surprise percentage."""
        if (
            self.actual_rev is not None
            and self.estimate_rev is not None
            and self.estimate_rev != 0
        ):
            return (self.actual_rev - self.estimate_rev) / self.estimate_rev * 100
        return None

    @property
    def ebitda_surprise_pct(self) -> Optional[Decimal]:
        """Calculate EBITDA surprise percentage."""
        if (
            self.actual_ebitda is not None
            and self.estimate_ebitda is not None
            and self.estimate_ebitda != 0
        ):
            return (self.actual_ebitda - self.estimate_ebitda) / self.estimate_ebitda * 100
        return None

    @property
    def fcf_surprise_pct(self) -> Optional[Decimal]:
        """Calculate FCF surprise percentage."""
        if (
            self.actual_fcf is not None
            and self.estimate_fcf is not None
            and self.estimate_fcf != 0
        ):
            return (self.actual_fcf - self.estimate_fcf) / self.estimate_fcf * 100
        return None
