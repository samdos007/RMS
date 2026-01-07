"""Guidance model for tracking management guidance vs actual results."""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Numeric, ForeignKey, Text, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.folder import Folder


class MetricType(str, Enum):
    """Type of financial metric."""
    REVENUE = "REVENUE"
    EPS = "EPS"
    EBITDA = "EBITDA"
    FCF = "FCF"
    OTHER = "OTHER"


class Guidance(Base, TimestampMixin):
    """
    Management guidance tracking.

    Tracks company guidance for specific periods and metrics,
    along with actual results when available.
    """

    __tablename__ = "guidance"
    __table_args__ = (
        UniqueConstraint(
            "folder_id",
            "ticker",
            "period",
            "metric",
            "guidance_period",
            name="uq_guidance_unique",
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

    # Period the guidance is for (e.g., "2025-Q1", "2025")
    period: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # What metric is being guided
    metric: Mapped[MetricType] = mapped_column(
        String(20),
        nullable=False,
    )

    # When the guidance was given (e.g., "2024-Q4")
    guidance_period: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Guidance range or point estimate
    guidance_low: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )
    guidance_high: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )
    guidance_point: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )

    # Actual result
    actual_result: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationship
    folder: Mapped["Folder"] = relationship(
        "Folder",
        back_populates="guidance",
    )

    @property
    def guidance_midpoint(self) -> Optional[Decimal]:
        """Calculate midpoint of guidance range."""
        if self.guidance_low is not None and self.guidance_high is not None:
            return (self.guidance_low + self.guidance_high) / 2
        return self.guidance_point

    @property
    def vs_guidance_low(self) -> Optional[Decimal]:
        """Calculate actual vs low end of guidance."""
        if self.actual_result is not None and self.guidance_low is not None:
            return self.actual_result - self.guidance_low
        return None

    @property
    def vs_guidance_high(self) -> Optional[Decimal]:
        """Calculate actual vs high end of guidance."""
        if self.actual_result is not None and self.guidance_high is not None:
            return self.actual_result - self.guidance_high
        return None

    @property
    def vs_guidance_midpoint(self) -> Optional[Decimal]:
        """Calculate actual vs midpoint of guidance."""
        midpoint = self.guidance_midpoint
        if self.actual_result is not None and midpoint is not None:
            return self.actual_result - midpoint
        return None
