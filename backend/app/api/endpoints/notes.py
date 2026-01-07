"""Note endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.idea import Idea
from app.models.folder import Folder
from app.models.note import Note, NoteType
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter(tags=["notes"])


@router.get("/ideas/{idea_id}/notes", response_model=List[NoteResponse])
async def list_notes_for_idea(
    idea_id: str,
    note_type: Optional[NoteType] = Query(None, description="Filter by note type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[NoteResponse]:
    """
    List all notes for an idea.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    query = db.query(Note).filter(Note.idea_id == idea_id)

    if note_type:
        query = query.filter(Note.note_type == note_type)

    notes = query.order_by(Note.created_at.desc()).all()

    return [NoteResponse.model_validate(note) for note in notes]


@router.get("/folders/{folder_id}/notes", response_model=List[NoteResponse])
async def list_notes_for_folder(
    folder_id: str,
    note_type: Optional[NoteType] = Query(None, description="Filter by note type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[NoteResponse]:
    """
    List all notes for a folder.
    """
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    query = db.query(Note).filter(Note.folder_id == folder_id)

    if note_type:
        query = query.filter(Note.note_type == note_type)

    notes = query.order_by(Note.created_at.desc()).all()

    return [NoteResponse.model_validate(note) for note in notes]


@router.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    request: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteResponse:
    """
    Create a new note for an idea or folder.
    """
    # Verify parent exists
    if request.idea_id:
        idea = db.query(Idea).filter(Idea.id == request.idea_id).first()
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Idea not found",
            )
    elif request.folder_id:
        folder = db.query(Folder).filter(Folder.id == request.folder_id).first()
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found",
            )

    note = Note(
        idea_id=request.idea_id,
        folder_id=request.folder_id,
        note_type=request.note_type,
        content_md=request.content_md,
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return NoteResponse.model_validate(note)


@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteResponse:
    """
    Get a note by ID.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    return NoteResponse.model_validate(note)


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    request: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteResponse:
    """
    Update a note.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)

    return NoteResponse.model_validate(note)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a note.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    db.delete(note)
    db.commit()


@router.get("/search/notes", response_model=List[NoteResponse])
async def search_notes(
    q: str = Query(..., min_length=1, description="Search query"),
    folder_id: Optional[str] = Query(None, description="Filter by folder"),
    note_type: Optional[NoteType] = Query(None, description="Filter by note type"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[NoteResponse]:
    """
    Search notes by content.

    Uses simple LIKE matching. For advanced search, consider SQLite FTS5.
    """
    query = db.query(Note).filter(Note.content_md.ilike(f"%{q}%"))

    if folder_id:
        query = query.join(Idea).filter(Idea.folder_id == folder_id)

    if note_type:
        query = query.filter(Note.note_type == note_type)

    notes = query.order_by(Note.created_at.desc()).limit(limit).all()

    return [NoteResponse.model_validate(note) for note in notes]
