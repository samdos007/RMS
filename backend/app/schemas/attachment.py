"""Attachment schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    """Schema for attachment response."""

    id: str
    folder_id: Optional[str] = None
    idea_id: Optional[str] = None
    filename: str
    mime_type: str
    size_bytes: int
    uploaded_at: datetime

    model_config = {"from_attributes": True}
