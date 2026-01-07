"""Price snapshot schemas."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.price_snapshot import PriceSource


class PriceSnapshotCreate(BaseModel):
    """Schema for creating a manual price snapshot."""

    timestamp: datetime
    price_primary: Decimal = Field(..., gt=0)
    price_secondary: Optional[Decimal] = Field(None, gt=0)
    note: Optional[str] = None


class PriceSnapshotResponse(BaseModel):
    """Schema for price snapshot response."""

    id: str
    idea_id: str
    timestamp: datetime
    price_primary: Decimal
    price_secondary: Optional[Decimal] = None
    source: PriceSource
    note: Optional[str] = None

    model_config = {"from_attributes": True}


class BackfillRequest(BaseModel):
    """Schema for backfill request."""

    start_date: Optional[date] = None  # Defaults to idea start_date if not provided
    end_date: Optional[date] = None  # Defaults to today if not provided


class BackfillResponse(BaseModel):
    """Schema for backfill response."""

    idea_id: str
    snapshots_created: int
    start_date: date
    end_date: date
    message: str


class PriceSnapshotListResponse(BaseModel):
    """Schema for price snapshot list response."""

    snapshots: List[PriceSnapshotResponse]
    total: int
