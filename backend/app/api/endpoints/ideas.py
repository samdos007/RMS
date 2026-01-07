"""Idea endpoints."""

from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.folder import Folder
from app.models.idea import Idea, IdeaStatus, TradeType
from app.models.note import Note, NoteType
from app.models.user import User
from app.schemas.idea import (
    CloseIdeaRequest,
    IdeaCreate,
    IdeaListResponse,
    IdeaResponse,
    IdeaStatusUpdate,
    IdeaUpdate,
)
from app.schemas.pnl import PnLHistoryResponse, PnLResponse
from app.services.pnl_service import PnLService
from app.services.price_service import PriceService

router = APIRouter(prefix="/ideas", tags=["ideas"])


def idea_to_response(
    idea: Idea,
    current_price_primary: Optional[Decimal] = None,
    current_price_secondary: Optional[Decimal] = None,
    pnl_percent: Optional[Decimal] = None,
    pnl_absolute: Optional[Decimal] = None,
) -> IdeaResponse:
    """Convert an Idea model to IdeaResponse."""
    return IdeaResponse(
        id=idea.id,
        folder_id=idea.folder_id,
        title=idea.title,
        trade_type=TradeType(idea.trade_type) if isinstance(idea.trade_type, str) else idea.trade_type,
        pair_orientation=idea.pair_orientation,
        status=IdeaStatus(idea.status) if isinstance(idea.status, str) else idea.status,
        start_date=idea.start_date,
        entry_price_primary=idea.entry_price_primary,
        entry_price_secondary=idea.entry_price_secondary,
        position_size=idea.position_size,
        horizon=idea.horizon,
        thesis_md=idea.thesis_md,
        catalysts=idea.catalysts or [],
        risks=idea.risks or [],
        kill_criteria_md=idea.kill_criteria_md,
        target_price_primary=idea.target_price_primary,
        stop_level_primary=idea.stop_level_primary,
        target_price_secondary=idea.target_price_secondary,
        stop_level_secondary=idea.stop_level_secondary,
        exit_price_primary=idea.exit_price_primary,
        exit_price_secondary=idea.exit_price_secondary,
        exit_date=idea.exit_date,
        created_at=idea.created_at,
        updated_at=idea.updated_at,
        current_price_primary=current_price_primary,
        current_price_secondary=current_price_secondary,
        pnl_percent=pnl_percent,
        pnl_absolute=pnl_absolute,
        folder_name=idea.folder.name if idea.folder else None,
    )


@router.get("", response_model=IdeaListResponse)
async def list_ideas(
    folder_id: Optional[str] = Query(None, description="Filter by folder"),
    status_filter: Optional[List[IdeaStatus]] = Query(None, alias="status", description="Filter by status"),
    include_pnl: bool = Query(False, description="Include current P&L calculations"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IdeaListResponse:
    """
    List ideas with optional filters.
    """
    query = db.query(Idea)

    if folder_id:
        query = query.filter(Idea.folder_id == folder_id)

    if status_filter:
        query = query.filter(Idea.status.in_([s.value for s in status_filter]))

    ideas = query.order_by(Idea.created_at.desc()).all()

    # Optionally calculate P&L for each idea
    idea_responses = []
    if include_pnl and ideas:
        price_service = PriceService(db)
        pnl_service = PnLService()

        # Collect all tickers needed
        tickers = set()
        for idea in ideas:
            if idea.folder:
                tickers.add(idea.folder.ticker_primary)
                if idea.folder.ticker_secondary:
                    tickers.add(idea.folder.ticker_secondary)

        # Batch fetch prices
        prices = price_service.get_current_prices(list(tickers))

        for idea in ideas:
            price_primary = prices.get(idea.folder.ticker_primary) if idea.folder else None
            price_secondary = prices.get(idea.folder.ticker_secondary) if idea.folder and idea.folder.ticker_secondary else None

            pnl_pct = None
            pnl_abs = None
            if price_primary is not None:
                try:
                    result = pnl_service.calculate_idea_pnl(idea, price_primary, price_secondary)
                    pnl_pct = result.pnl_percent
                    pnl_abs = result.pnl_absolute
                except ValueError:
                    pass

            idea_responses.append(idea_to_response(idea, price_primary, price_secondary, pnl_pct, pnl_abs))
    else:
        idea_responses = [idea_to_response(idea) for idea in ideas]

    return IdeaListResponse(
        ideas=idea_responses,
        total=len(idea_responses),
    )


@router.get("/{idea_id}", response_model=IdeaResponse)
async def get_idea(
    idea_id: str,
    include_pnl: bool = Query(True, description="Include current P&L calculation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IdeaResponse:
    """
    Get an idea by ID.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    price_primary = None
    price_secondary = None
    pnl_pct = None
    pnl_abs = None

    if include_pnl and idea.folder:
        price_service = PriceService(db)
        pnl_service = PnLService()

        tickers = [idea.folder.ticker_primary]
        if idea.folder.ticker_secondary:
            tickers.append(idea.folder.ticker_secondary)

        prices = price_service.get_current_prices(tickers)
        price_primary = prices.get(idea.folder.ticker_primary)
        price_secondary = prices.get(idea.folder.ticker_secondary)

        if price_primary is not None:
            try:
                result = pnl_service.calculate_idea_pnl(idea, price_primary, price_secondary)
                pnl_pct = result.pnl_percent
                pnl_abs = result.pnl_absolute
            except ValueError:
                pass

    return idea_to_response(idea, price_primary, price_secondary, pnl_pct, pnl_abs)


@router.post("", response_model=IdeaResponse, status_code=status.HTTP_201_CREATED)
async def create_idea(
    request: IdeaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IdeaResponse:
    """
    Create a new idea.
    """
    # Verify folder exists
    folder = db.query(Folder).filter(Folder.id == request.folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    # Validate pair trade requirements
    if request.trade_type == TradeType.PAIR_LONG_SHORT:
        if folder.type != "PAIR":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pair trades can only be created in PAIR folders",
            )

    idea = Idea(
        folder_id=request.folder_id,
        title=request.title,
        trade_type=request.trade_type,
        pair_orientation=request.pair_orientation,
        status=IdeaStatus.DRAFT,
        start_date=request.start_date,
        entry_price_primary=request.entry_price_primary,
        entry_price_secondary=request.entry_price_secondary,
        position_size=request.position_size,
        horizon=request.horizon,
        thesis_md=request.thesis_md,
        catalysts=request.catalysts,
        risks=request.risks,
        kill_criteria_md=request.kill_criteria_md,
        target_price_primary=request.target_price_primary,
        stop_level_primary=request.stop_level_primary,
        target_price_secondary=request.target_price_secondary,
        stop_level_secondary=request.stop_level_secondary,
    )

    db.add(idea)
    db.commit()
    db.refresh(idea)

    return idea_to_response(idea)


@router.put("/{idea_id}", response_model=IdeaResponse)
async def update_idea(
    idea_id: str,
    request: IdeaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IdeaResponse:
    """
    Update an idea.

    Note: trade_type, pair_orientation, entry prices, and start_date cannot be changed.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    # Update allowed fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(idea, field, value)

    db.commit()
    db.refresh(idea)

    return idea_to_response(idea)


@router.patch("/{idea_id}/status", response_model=IdeaResponse)
async def update_idea_status(
    idea_id: str,
    request: IdeaStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IdeaResponse:
    """
    Update idea status (non-closing statuses only).

    For CLOSED or KILLED status, use the close endpoint.
    """
    if request.status in (IdeaStatus.CLOSED, IdeaStatus.KILLED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use POST /ideas/{id}/close for closing an idea",
        )

    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    idea.status = request.status
    db.commit()
    db.refresh(idea)

    return idea_to_response(idea)


@router.post("/{idea_id}/close", response_model=IdeaResponse)
async def close_idea(
    idea_id: str,
    request: CloseIdeaRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IdeaResponse:
    """
    Close an idea (CLOSED or KILLED status).

    Requires exit prices and optionally a postmortem note.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    if idea.is_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idea is already closed",
        )

    # Validate pair trade exit price
    if idea.is_pair and not request.exit_price_secondary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="exit_price_secondary required for pair trades",
        )

    # Update idea
    idea.status = request.status
    idea.exit_price_primary = request.exit_price_primary
    idea.exit_price_secondary = request.exit_price_secondary
    idea.exit_date = request.exit_date

    # Create postmortem note if provided
    if request.postmortem_note:
        note = Note(
            idea_id=idea.id,
            note_type=NoteType.POSTMORTEM,
            content_md=request.postmortem_note,
        )
        db.add(note)

    db.commit()
    db.refresh(idea)

    return idea_to_response(idea)


@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_idea(
    idea_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete an idea and all its contents.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    db.delete(idea)
    db.commit()


@router.get("/{idea_id}/pnl", response_model=PnLResponse)
async def get_idea_pnl(
    idea_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PnLResponse:
    """
    Get detailed P&L calculation for an idea.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    price_service = PriceService(db)
    pnl_service = PnLService()

    tickers = [idea.folder.ticker_primary]
    if idea.folder.ticker_secondary:
        tickers.append(idea.folder.ticker_secondary)

    prices = price_service.get_current_prices(tickers)
    price_primary = prices.get(idea.folder.ticker_primary)
    price_secondary = prices.get(idea.folder.ticker_secondary)

    if price_primary is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to fetch price for {idea.folder.ticker_primary}",
        )

    if idea.is_pair and price_secondary is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to fetch price for {idea.folder.ticker_secondary}",
        )

    return pnl_service.get_pnl_response(idea, price_primary, price_secondary)


@router.get("/{idea_id}/pnl/history", response_model=PnLHistoryResponse)
async def get_idea_pnl_history(
    idea_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PnLHistoryResponse:
    """
    Get P&L history for an idea based on stored price snapshots.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    pnl_service = PnLService()
    return pnl_service.get_pnl_history(idea, idea.price_snapshots)
