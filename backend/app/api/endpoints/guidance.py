"""Guidance endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.guidance import Guidance
from app.models.folder import Folder
from app.models.user import User
from app.schemas.guidance import (
    GuidanceCreate,
    GuidanceListResponse,
    GuidanceResponse,
    GuidanceUpdate,
)

router = APIRouter(tags=["guidance"])


def guidance_to_response(guidance: Guidance) -> GuidanceResponse:
    """Convert Guidance model to response schema."""
    return GuidanceResponse(
        id=guidance.id,
        folder_id=guidance.folder_id,
        ticker=guidance.ticker,
        period=guidance.period,
        metric=guidance.metric,
        guidance_period=guidance.guidance_period,
        guidance_low=guidance.guidance_low,
        guidance_high=guidance.guidance_high,
        guidance_point=guidance.guidance_point,
        actual_result=guidance.actual_result,
        guidance_midpoint=guidance.guidance_midpoint,
        vs_guidance_low=guidance.vs_guidance_low,
        vs_guidance_high=guidance.vs_guidance_high,
        vs_guidance_midpoint=guidance.vs_guidance_midpoint,
        notes=guidance.notes,
        created_at=guidance.created_at,
        updated_at=guidance.updated_at,
    )


@router.get("/folders/{folder_id}/guidance", response_model=GuidanceListResponse)
async def list_guidance(
    folder_id: str,
    ticker: Optional[str] = Query(None, description="Filter by specific ticker"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GuidanceListResponse:
    """
    List guidance records for a folder.

    For PAIR folders, you can filter by ticker to see guidance for just one leg.
    """
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    query = db.query(Guidance).filter(Guidance.folder_id == folder_id)

    if ticker:
        query = query.filter(Guidance.ticker == ticker.upper())

    guidance_list = query.order_by(Guidance.period.desc(), Guidance.metric).all()

    return GuidanceListResponse(
        guidance=[guidance_to_response(g) for g in guidance_list],
        total=len(guidance_list),
    )


@router.post("/guidance", response_model=GuidanceResponse, status_code=status.HTTP_201_CREATED)
async def create_guidance(
    request: GuidanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GuidanceResponse:
    """
    Create a new guidance record.
    """
    folder = db.query(Folder).filter(Folder.id == request.folder_id).first()
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    # Validate ticker belongs to folder
    if request.ticker.upper() not in folder.tickers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker {request.ticker} does not belong to folder {folder.name}",
        )

    # Check for duplicate
    existing = (
        db.query(Guidance)
        .filter(
            Guidance.folder_id == request.folder_id,
            Guidance.ticker == request.ticker.upper(),
            Guidance.period == request.period,
            Guidance.metric == request.metric,
            Guidance.guidance_period == request.guidance_period,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Guidance for {request.ticker} {request.period} {request.metric} from {request.guidance_period} already exists",
        )

    guidance = Guidance(
        folder_id=request.folder_id,
        ticker=request.ticker.upper(),
        period=request.period,
        metric=request.metric,
        guidance_period=request.guidance_period,
        guidance_low=request.guidance_low,
        guidance_high=request.guidance_high,
        guidance_point=request.guidance_point,
        actual_result=request.actual_result,
        notes=request.notes,
    )

    db.add(guidance)
    db.commit()
    db.refresh(guidance)

    return guidance_to_response(guidance)


@router.get("/guidance/{guidance_id}", response_model=GuidanceResponse)
async def get_guidance(
    guidance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GuidanceResponse:
    """
    Get guidance by ID.
    """
    guidance = db.query(Guidance).filter(Guidance.id == guidance_id).first()
    if not guidance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guidance not found",
        )

    return guidance_to_response(guidance)


@router.put("/guidance/{guidance_id}", response_model=GuidanceResponse)
async def update_guidance(
    guidance_id: str,
    request: GuidanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GuidanceResponse:
    """
    Update guidance data.
    """
    guidance = db.query(Guidance).filter(Guidance.id == guidance_id).first()
    if not guidance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guidance not found",
        )

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(guidance, field, value)

    db.commit()
    db.refresh(guidance)

    return guidance_to_response(guidance)


@router.delete("/guidance/{guidance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_guidance(
    guidance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete guidance record.
    """
    guidance = db.query(Guidance).filter(Guidance.id == guidance_id).first()
    if not guidance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guidance not found",
        )

    db.delete(guidance)
    db.commit()
