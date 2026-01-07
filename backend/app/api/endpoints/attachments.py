"""Attachment endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.attachment import Attachment
from app.models.folder import Folder
from app.models.idea import Idea
from app.models.user import User
from app.schemas.attachment import AttachmentResponse
from app.services.file_service import FileService

router = APIRouter(tags=["attachments"])


@router.get("/folders/{folder_id}/attachments", response_model=List[AttachmentResponse])
async def list_folder_attachments(
    folder_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[AttachmentResponse]:
    """
    List all attachments for a folder.
    """
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    attachments = (
        db.query(Attachment)
        .filter(Attachment.folder_id == folder_id)
        .order_by(Attachment.uploaded_at.desc())
        .all()
    )

    return [AttachmentResponse.model_validate(a) for a in attachments]


@router.get("/ideas/{idea_id}/attachments", response_model=List[AttachmentResponse])
async def list_idea_attachments(
    idea_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[AttachmentResponse]:
    """
    List all attachments for an idea.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    attachments = (
        db.query(Attachment)
        .filter(Attachment.idea_id == idea_id)
        .order_by(Attachment.uploaded_at.desc())
        .all()
    )

    return [AttachmentResponse.model_validate(a) for a in attachments]


@router.post(
    "/folders/{folder_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_folder_attachment(
    folder_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AttachmentResponse:
    """
    Upload an attachment to a folder.
    """
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    file_service = FileService(db)
    attachment = await file_service.save_file(file, folder_id=folder_id)

    return AttachmentResponse.model_validate(attachment)


@router.post(
    "/ideas/{idea_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_idea_attachment(
    idea_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AttachmentResponse:
    """
    Upload an attachment to an idea.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    file_service = FileService(db)
    attachment = await file_service.save_file(file, idea_id=idea_id)

    return AttachmentResponse.model_validate(attachment)


@router.get("/attachments/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AttachmentResponse:
    """
    Get attachment metadata.
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    return AttachmentResponse.model_validate(attachment)


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """
    Download an attachment file.
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    file_service = FileService(db)
    file_path = file_service.get_file_path(attachment)

    return FileResponse(
        path=file_path,
        filename=attachment.filename,
        media_type=attachment.mime_type,
    )


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete an attachment and its file.
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    file_service = FileService(db)
    file_service.delete_file(attachment)
