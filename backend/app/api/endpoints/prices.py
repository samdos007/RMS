"""Price endpoints."""

from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.idea import Idea
from app.models.price_snapshot import PriceSnapshot
from app.models.user import User
from app.schemas.price_snapshot import (
    BackfillRequest,
    BackfillResponse,
    PriceSnapshotCreate,
    PriceSnapshotResponse,
)
from app.services.price_service import PriceService

router = APIRouter(tags=["prices"])


@router.get("/ideas/{idea_id}/prices", response_model=List[PriceSnapshotResponse])
async def list_price_snapshots(
    idea_id: str,
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[PriceSnapshotResponse]:
    """
    List price snapshots for an idea.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    query = db.query(PriceSnapshot).filter(PriceSnapshot.idea_id == idea_id)

    if start_date:
        query = query.filter(
            PriceSnapshot.timestamp >= datetime.combine(start_date, datetime.min.time())
        )
    if end_date:
        query = query.filter(
            PriceSnapshot.timestamp <= datetime.combine(end_date, datetime.max.time())
        )

    snapshots = query.order_by(PriceSnapshot.timestamp.desc()).limit(limit).all()

    return [PriceSnapshotResponse.model_validate(s) for s in snapshots]


@router.post(
    "/ideas/{idea_id}/prices",
    response_model=PriceSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_manual_snapshot(
    idea_id: str,
    request: PriceSnapshotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PriceSnapshotResponse:
    """
    Add a manual price snapshot.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    price_service = PriceService(db)

    try:
        snapshot = price_service.add_manual_snapshot(
            idea=idea,
            timestamp=request.timestamp,
            price_primary=request.price_primary,
            price_secondary=request.price_secondary,
            note=request.note,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return PriceSnapshotResponse.model_validate(snapshot)


@router.post("/ideas/{idea_id}/prices/fetch", response_model=PriceSnapshotResponse)
async def fetch_latest_prices(
    idea_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PriceSnapshotResponse:
    """
    Fetch latest prices from yfinance and create a snapshot.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    price_service = PriceService(db)
    snapshot = price_service.fetch_latest_and_create_snapshot(idea)

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch prices from market data provider",
        )

    return PriceSnapshotResponse.model_validate(snapshot)


@router.post("/ideas/{idea_id}/prices/backfill", response_model=BackfillResponse)
async def backfill_prices(
    idea_id: str,
    request: Optional[BackfillRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BackfillResponse:
    """
    Backfill historical prices for an idea.

    This is idempotent - it will only create snapshots for dates that don't
    already have one.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found",
        )

    start_date = request.start_date if request and request.start_date else idea.start_date
    end_date = request.end_date if request and request.end_date else date.today()

    price_service = PriceService(db)
    created_count = price_service.backfill_prices_idempotent(
        idea=idea,
        start_date=start_date,
        end_date=end_date,
    )

    return BackfillResponse(
        idea_id=idea_id,
        snapshots_created=created_count,
        start_date=start_date,
        end_date=end_date,
        message=f"Created {created_count} new price snapshots",
    )


@router.delete(
    "/ideas/{idea_id}/prices/{snapshot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_price_snapshot(
    idea_id: str,
    snapshot_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a price snapshot.
    """
    snapshot = (
        db.query(PriceSnapshot)
        .filter(PriceSnapshot.id == snapshot_id, PriceSnapshot.idea_id == idea_id)
        .first()
    )

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price snapshot not found",
        )

    db.delete(snapshot)
    db.commit()
