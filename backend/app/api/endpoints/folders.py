"""Folder endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.folder import Folder, FolderType
from app.models.idea import IdeaStatus
from app.models.user import User
from app.schemas.folder import (
    FolderCreate,
    FolderListResponse,
    FolderResponse,
    FolderUpdate,
    ThemeOption,
    ThemeTickerPerformance,
    TickerPnL,
)
from app.services.price_service import PriceService

router = APIRouter(prefix="/folders", tags=["folders"])


def folder_to_response(folder: Folder) -> FolderResponse:
    """Convert a Folder model to FolderResponse."""
    idea_count = len(folder.ideas)
    active_count = sum(
        1 for idea in folder.ideas
        if idea.status not in (IdeaStatus.CLOSED, IdeaStatus.KILLED)
    )

    # Convert theme_tickers JSON to TickerPnL objects
    theme_tickers = []
    if folder.type == FolderType.THEME and folder.theme_tickers:
        theme_tickers = [
            TickerPnL(ticker=t["ticker"], pnl=t.get("pnl"))
            for t in folder.theme_tickers
        ]

    return FolderResponse(
        id=folder.id,
        type=FolderType(folder.type) if isinstance(folder.type, str) else folder.type,
        ticker_primary=folder.ticker_primary,
        ticker_secondary=folder.ticker_secondary,
        theme_name=folder.theme_name,
        theme_date=folder.theme_date,
        theme_thesis=folder.theme_thesis,
        theme_tickers=theme_tickers,
        theme_ids=folder.theme_ids or [],
        name=folder.name,
        description=folder.description,
        tags=folder.tags or [],
        tickers=folder.tickers,
        created_at=folder.created_at,
        updated_at=folder.updated_at,
        idea_count=idea_count,
        active_idea_count=active_count,
    )


@router.get("", response_model=FolderListResponse)
async def list_folders(
    search: Optional[str] = Query(None, description="Search by ticker or tag"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FolderListResponse:
    """
    List all folders with optional search and tag filters.
    """
    query = db.query(Folder)

    if search:
        search_term = f"%{search.upper()}%"
        query = query.filter(
            (Folder.ticker_primary.ilike(search_term))
            | (Folder.ticker_secondary.ilike(search_term))
            | (Folder.theme_name.ilike(search_term))
        )

    if tags:
        # Filter folders that have any of the specified tags
        for tag in tags:
            query = query.filter(Folder.tags.contains([tag]))

    folders = query.order_by(Folder.ticker_primary).all()

    return FolderListResponse(
        folders=[folder_to_response(f) for f in folders],
        total=len(folders),
    )


@router.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FolderResponse:
    """
    Get a folder by ID.
    """
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    return folder_to_response(folder)


@router.post("", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    request: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FolderResponse:
    """
    Create a new folder.
    """
    # Check for duplicate
    if request.type == FolderType.THEME:
        # Check for duplicate theme name (case-insensitive)
        existing = db.query(Folder).filter(
            Folder.type == FolderType.THEME,
            func.lower(Folder.theme_name) == request.theme_name.lower()
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A theme with this name already exists",
            )

        # Create THEME folder
        folder = Folder(
            type=FolderType.THEME,
            theme_name=request.theme_name,
            theme_date=request.theme_date,
            theme_thesis=request.theme_thesis,
            theme_tickers=[
                {"ticker": t.ticker.upper(), "pnl": float(t.pnl) if t.pnl else None}
                for t in request.theme_tickers
            ],
            description=request.description,
            tags=request.tags,
        )
    else:
        # Check for duplicate ticker combination (SINGLE/PAIR)
        existing = db.query(Folder).filter(
            Folder.ticker_primary == request.ticker_primary.upper()
        )
        if request.ticker_secondary:
            existing = existing.filter(
                Folder.ticker_secondary == request.ticker_secondary.upper()
            )
        else:
            existing = existing.filter(Folder.ticker_secondary.is_(None))

        if existing.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A folder with this ticker combination already exists",
            )

        # Create SINGLE/PAIR folder
        folder = Folder(
            type=request.type,
            ticker_primary=request.ticker_primary.upper(),
            ticker_secondary=request.ticker_secondary.upper() if request.ticker_secondary else None,
            description=request.description,
            tags=request.tags,
        )

    db.add(folder)
    db.commit()
    db.refresh(folder)

    return folder_to_response(folder)


@router.put("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: str,
    request: FolderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FolderResponse:
    """
    Update a folder.

    Note: ticker_primary and ticker_secondary cannot be changed after creation.
    """
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    # Common fields
    if request.description is not None:
        folder.description = request.description
    if request.tags is not None:
        folder.tags = request.tags

    # THEME-specific updates
    if folder.type == FolderType.THEME:
        if request.theme_date is not None:
            folder.theme_date = request.theme_date
        if request.theme_thesis is not None:
            folder.theme_thesis = request.theme_thesis
        if request.theme_tickers is not None:
            folder.theme_tickers = [
                {"ticker": t.ticker.upper(), "pnl": float(t.pnl) if t.pnl else None}
                for t in request.theme_tickers
            ]

    db.commit()
    db.refresh(folder)

    return folder_to_response(folder)


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a folder and all its contents.

    This cascades to delete all ideas, notes, attachments, and earnings.
    If deleting a THEME folder, also removes theme associations from all linked folders.
    """
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    # If deleting a THEME, remove from all associated folders
    if folder.type == FolderType.THEME:
        associated = db.query(Folder).filter(
            Folder.theme_ids.contains([folder_id])
        ).all()
        for f in associated:
            f.theme_ids = [tid for tid in f.theme_ids if tid != folder_id]

    db.delete(folder)
    db.commit()


@router.get("/themes/autocomplete", response_model=List[ThemeOption])
async def autocomplete_themes(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ThemeOption]:
    """
    Get list of themes for autocomplete/selection.
    """
    query = db.query(Folder).filter(Folder.type == FolderType.THEME)

    if search:
        query = query.filter(Folder.theme_name.ilike(f"%{search}%"))

    themes = query.order_by(Folder.theme_name).limit(20).all()

    return [
        ThemeOption(
            id=theme.id,
            name=theme.theme_name,
            date=theme.theme_date,
            ticker_count=len(theme.theme_tickers or []),
        )
        for theme in themes
    ]


@router.post("/{folder_id}/themes")
async def add_folder_to_themes(
    folder_id: str,
    theme_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add a ticker folder to one or more themes.
    """
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    if folder.type == FolderType.THEME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add themes to a theme folder",
        )

    # Verify all theme_ids exist and are THEME type
    themes = db.query(Folder).filter(
        Folder.id.in_(theme_ids),
        Folder.type == FolderType.THEME
    ).all()

    if len(themes) != len(theme_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid theme IDs provided",
        )

    # Update folder's theme_ids (merge with existing)
    current_themes = set(folder.theme_ids or [])
    current_themes.update(theme_ids)
    folder.theme_ids = list(current_themes)

    db.commit()

    return {"message": "Themes added", "theme_ids": folder.theme_ids}


@router.get("/themes/{theme_id}/folders", response_model=List[FolderResponse])
async def get_folders_in_theme(
    theme_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[FolderResponse]:
    """
    Get all ticker folders that belong to a theme.
    """
    # Verify theme exists
    theme = db.query(Folder).filter(
        Folder.id == theme_id,
        Folder.type == FolderType.THEME
    ).first()
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found",
        )

    # Find all folders with this theme_id
    folders = db.query(Folder).filter(
        Folder.theme_ids.contains([theme_id])
    ).all()

    return [folder_to_response(f) for f in folders]


@router.get("/{folder_id}/performance", response_model=List[ThemeTickerPerformance])
async def get_theme_performance(
    folder_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ThemeTickerPerformance]:
    """
    Get performance data for all tickers in a theme folder.

    Fetches historical prices on theme_date and current prices,
    calculates P&L for each ticker.
    """
    # Get folder and verify it's a THEME
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    if folder.type != FolderType.THEME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Performance endpoint only available for THEME folders",
        )

    if not folder.theme_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Theme date is required to calculate performance",
        )

    # Get tickers from theme
    tickers = [t["ticker"] for t in (folder.theme_tickers or [])]
    if not tickers:
        return []

    # Use price service to get performance data
    price_service = PriceService(db)
    performance_data = price_service.get_theme_ticker_performance(
        tickers=tickers,
        theme_date=folder.theme_date,
    )

    return [ThemeTickerPerformance(**data) for data in performance_data]
