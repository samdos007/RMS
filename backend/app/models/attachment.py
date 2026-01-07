"""Attachment model for file uploads."""

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.folder import Folder
    from app.models.idea import Idea


class Attachment(Base):
    """
    File attachment that can belong to either a folder or an idea.

    Only one of folder_id or idea_id should be set (not both, not neither).
    """

    __tablename__ = "attachments"
    __table_args__ = (
        CheckConstraint(
            "(folder_id IS NOT NULL AND idea_id IS NULL) OR "
            "(folder_id IS NULL AND idea_id IS NOT NULL)",
            name="attachment_belongs_to_one",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    folder_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    idea_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    folder: Mapped[Optional["Folder"]] = relationship(
        "Folder",
        back_populates="attachments",
        foreign_keys=[folder_id],
    )
    idea: Mapped[Optional["Idea"]] = relationship(
        "Idea",
        back_populates="attachments",
        foreign_keys=[idea_id],
    )
