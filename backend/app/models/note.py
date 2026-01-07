"""Note model for idea and folder notes."""

import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.idea import Idea
    from app.models.folder import Folder


class NoteType(str, Enum):
    """Type of note."""
    GENERAL = "GENERAL"
    EARNINGS = "EARNINGS"
    CHANNEL_CHECK = "CHANNEL_CHECK"
    VALUATION = "VALUATION"
    RISK = "RISK"
    POSTMORTEM = "POSTMORTEM"


class Note(Base, TimestampMixin):
    """
    Note attached to an idea or folder.

    Supports markdown content and categorization by type.
    Either idea_id or folder_id must be set (not both).
    """

    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    idea_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    folder_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    note_type: Mapped[NoteType] = mapped_column(
        String(20),
        nullable=False,
        default=NoteType.GENERAL,
    )
    content_md: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Relationships
    idea: Mapped[Optional["Idea"]] = relationship(
        "Idea",
        back_populates="notes",
    )
    folder: Mapped[Optional["Folder"]] = relationship(
        "Folder",
        back_populates="notes",
    )
