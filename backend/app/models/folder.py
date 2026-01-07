"""Folder model for organizing investment research."""

import uuid
from datetime import date
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, JSON, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.idea import Idea
    from app.models.attachment import Attachment
    from app.models.earnings import Earnings
    from app.models.guidance import Guidance
    from app.models.note import Note


class FolderType(str, Enum):
    """Type of folder - single ticker, pair, or theme."""
    SINGLE = "SINGLE"
    PAIR = "PAIR"
    THEME = "THEME"


class Folder(Base, TimestampMixin):
    """
    Folder for organizing investment research.

    Each folder represents either a single ticker, a ticker pair, or an investment theme.
    """

    __tablename__ = "folders"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    type: Mapped[FolderType] = mapped_column(
        String(20),
        nullable=False,
        default=FolderType.SINGLE,
    )

    # SINGLE/PAIR fields
    ticker_primary: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,  # Now nullable for THEME folders
        index=True,
    )
    ticker_secondary: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    # THEME fields
    theme_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    theme_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    theme_thesis: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    theme_tickers: Mapped[List[dict]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    # Theme associations (for SINGLE/PAIR folders to link to themes)
    theme_ids: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    # Common fields
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    tags: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    # Relationships
    ideas: Mapped[List["Idea"]] = relationship(
        "Idea",
        back_populates="folder",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment",
        back_populates="folder",
        cascade="all, delete-orphan",
        foreign_keys="Attachment.folder_id",
        lazy="selectin",
    )
    earnings: Mapped[List["Earnings"]] = relationship(
        "Earnings",
        back_populates="folder",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    guidance: Mapped[List["Guidance"]] = relationship(
        "Guidance",
        back_populates="folder",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    notes: Mapped[List["Note"]] = relationship(
        "Note",
        back_populates="folder",
        cascade="all, delete-orphan",
        foreign_keys="Note.folder_id",
        lazy="selectin",
    )

    @property
    def name(self) -> str:
        """Computed display name for the folder."""
        if self.type == FolderType.THEME:
            return self.theme_name or "Unnamed Theme"
        if self.type == FolderType.PAIR and self.ticker_secondary:
            return f"{self.ticker_primary}/{self.ticker_secondary}"
        return self.ticker_primary or "Unknown"

    @property
    def tickers(self) -> List[str]:
        """List of all tickers in this folder."""
        if self.type == FolderType.THEME:
            return [t["ticker"] for t in (self.theme_tickers or [])]

        tickers = []
        if self.ticker_primary:
            tickers.append(self.ticker_primary)
        if self.ticker_secondary:
            tickers.append(self.ticker_secondary)
        return tickers
