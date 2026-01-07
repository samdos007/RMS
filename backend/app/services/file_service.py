"""File service for attachment handling."""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.attachment import Attachment


class FileService:
    """
    Service for handling file uploads and storage.
    """

    def __init__(self, db: Session):
        self.db = db

    def _get_safe_filename(self, filename: str) -> str:
        """Generate a safe filename by prepending a UUID."""
        ext = Path(filename).suffix.lower()
        safe_name = f"{uuid.uuid4()}{ext}"
        return safe_name

    def _validate_file(self, file: UploadFile) -> None:
        """Validate file type and size."""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        ext = Path(file.filename).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}",
            )

    async def save_file(
        self,
        file: UploadFile,
        folder_id: Optional[str] = None,
        idea_id: Optional[str] = None,
    ) -> Attachment:
        """
        Save an uploaded file and create attachment record.

        Args:
            file: The uploaded file
            folder_id: ID of folder to attach to (exclusive with idea_id)
            idea_id: ID of idea to attach to (exclusive with folder_id)

        Returns:
            Created Attachment model
        """
        if not folder_id and not idea_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either folder_id or idea_id must be provided",
            )

        if folder_id and idea_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot attach to both folder and idea",
            )

        self._validate_file(file)

        # Ensure upload directory exists
        settings.ensure_directories()

        # Generate safe filename and path
        safe_filename = self._get_safe_filename(file.filename or "upload")
        file_path = settings.upload_dir / safe_filename

        # Read and save file content
        content = await file.read()

        # Check file size
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB",
            )

        # Write file to disk
        with open(file_path, "wb") as f:
            f.write(content)

        # Create attachment record
        attachment = Attachment(
            folder_id=folder_id,
            idea_id=idea_id,
            filename=file.filename or "upload",
            mime_type=file.content_type or "application/octet-stream",
            size_bytes=len(content),
            storage_path=str(file_path),
            uploaded_at=datetime.utcnow(),
        )

        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)

        return attachment

    def get_file_path(self, attachment: Attachment) -> Path:
        """Get the file path for an attachment."""
        path = Path(attachment.storage_path)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk",
            )
        return path

    def delete_file(self, attachment: Attachment) -> None:
        """
        Delete an attachment and its file from disk.
        """
        # Delete file from disk
        try:
            path = Path(attachment.storage_path)
            if path.exists():
                os.remove(path)
        except Exception:
            pass  # File might already be deleted

        # Delete database record
        self.db.delete(attachment)
        self.db.commit()
