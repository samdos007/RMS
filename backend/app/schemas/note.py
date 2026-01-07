"""Note schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.models.note import NoteType


class NoteCreate(BaseModel):
    """Schema for creating a note."""

    idea_id: Optional[str] = None
    folder_id: Optional[str] = None
    note_type: NoteType = NoteType.GENERAL
    content_md: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_parent(self) -> "NoteCreate":
        """Ensure exactly one of idea_id or folder_id is set."""
        if self.idea_id and self.folder_id:
            raise ValueError("Cannot set both idea_id and folder_id")
        if not self.idea_id and not self.folder_id:
            raise ValueError("Must set either idea_id or folder_id")
        return self


class NoteUpdate(BaseModel):
    """Schema for updating a note."""

    note_type: Optional[NoteType] = None
    content_md: Optional[str] = Field(None, min_length=1)


class NoteResponse(BaseModel):
    """Schema for note response."""

    id: str
    idea_id: Optional[str] = None
    folder_id: Optional[str] = None
    note_type: NoteType
    content_md: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
