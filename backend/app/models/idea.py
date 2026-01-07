"""Idea model for trade ideas."""

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, Date, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.folder import Folder
    from app.models.note import Note
    from app.models.attachment import Attachment
    from app.models.price_snapshot import PriceSnapshot


class TradeType(str, Enum):
    """Type of trade."""
    LONG = "LONG"
    SHORT = "SHORT"
    PAIR_LONG_SHORT = "PAIR_LONG_SHORT"


class PairOrientation(str, Enum):
    """For pair trades, which leg is long."""
    LONG_PRIMARY_SHORT_SECONDARY = "LONG_PRIMARY_SHORT_SECONDARY"
    SHORT_PRIMARY_LONG_SECONDARY = "SHORT_PRIMARY_LONG_SECONDARY"


class IdeaStatus(str, Enum):
    """Status of the trade idea."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SCALED_UP = "SCALED_UP"
    TRIMMED = "TRIMMED"
    CLOSED = "CLOSED"
    KILLED = "KILLED"


class Horizon(str, Enum):
    """Investment horizon."""
    EVENT = "EVENT"
    THREE_TO_SIX_MONTHS = "3_6MO"
    SIX_TO_TWELVE_MONTHS = "6_12MO"
    SECULAR = "SECULAR"
    OTHER = "OTHER"


class Idea(Base, TimestampMixin):
    """
    Trade idea with thesis, position details, and P&L tracking.
    """

    __tablename__ = "ideas"

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

    # Basic info
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    trade_type: Mapped[TradeType] = mapped_column(
        String(20),
        nullable=False,
    )
    pair_orientation: Mapped[Optional[PairOrientation]] = mapped_column(
        String(40),
        nullable=True,
    )
    status: Mapped[IdeaStatus] = mapped_column(
        String(20),
        nullable=False,
        default=IdeaStatus.DRAFT,
    )
    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # Entry prices
    entry_price_primary: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=False,
    )
    entry_price_secondary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )

    # Position sizing
    position_size: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=False,
        default=Decimal("0"),
    )

    # Investment horizon
    horizon: Mapped[Horizon] = mapped_column(
        String(20),
        nullable=False,
        default=Horizon.OTHER,
    )

    # Thesis and analysis
    thesis_md: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    catalysts: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    risks: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    kill_criteria_md: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Target/Stop levels (primary)
    target_price_primary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )
    stop_level_primary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )

    # Target/Stop levels (secondary, for pairs)
    target_price_secondary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )
    stop_level_secondary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )

    # Exit data (required when closing)
    exit_price_primary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )
    exit_price_secondary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=18, scale=6),
        nullable=True,
    )
    exit_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    # Relationships
    folder: Mapped["Folder"] = relationship(
        "Folder",
        back_populates="ideas",
    )
    notes: Mapped[List["Note"]] = relationship(
        "Note",
        back_populates="idea",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment",
        back_populates="idea",
        cascade="all, delete-orphan",
        foreign_keys="Attachment.idea_id",
        lazy="selectin",
    )
    price_snapshots: Mapped[List["PriceSnapshot"]] = relationship(
        "PriceSnapshot",
        back_populates="idea",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="PriceSnapshot.timestamp.desc()",
    )

    @property
    def is_pair(self) -> bool:
        """Check if this is a pair trade."""
        return self.trade_type == TradeType.PAIR_LONG_SHORT

    @property
    def is_closed(self) -> bool:
        """Check if the idea is closed or killed."""
        return self.status in (IdeaStatus.CLOSED, IdeaStatus.KILLED)
