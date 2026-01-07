"""Guidance schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.guidance import MetricType


class GuidanceCreate(BaseModel):
    """Schema for creating guidance data."""

    folder_id: str
    ticker: str = Field(..., min_length=1, max_length=20)
    period: str = Field(..., min_length=1, max_length=20)
    metric: MetricType
    guidance_period: str = Field(..., min_length=1, max_length=20)
    guidance_low: Optional[Decimal] = None
    guidance_high: Optional[Decimal] = None
    guidance_point: Optional[Decimal] = None
    actual_result: Optional[Decimal] = None
    notes: Optional[str] = None


class GuidanceUpdate(BaseModel):
    """Schema for updating guidance data."""

    period: Optional[str] = None
    metric: Optional[MetricType] = None
    guidance_period: Optional[str] = None
    guidance_low: Optional[Decimal] = None
    guidance_high: Optional[Decimal] = None
    guidance_point: Optional[Decimal] = None
    actual_result: Optional[Decimal] = None
    notes: Optional[str] = None


class GuidanceResponse(BaseModel):
    """Schema for guidance response."""

    id: str
    folder_id: str
    ticker: str
    period: str
    metric: MetricType
    guidance_period: str
    guidance_low: Optional[Decimal] = None
    guidance_high: Optional[Decimal] = None
    guidance_point: Optional[Decimal] = None
    actual_result: Optional[Decimal] = None
    guidance_midpoint: Optional[Decimal] = None
    vs_guidance_low: Optional[Decimal] = None
    vs_guidance_high: Optional[Decimal] = None
    vs_guidance_midpoint: Optional[Decimal] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GuidanceListResponse(BaseModel):
    """Schema for guidance list response."""

    guidance: List[GuidanceResponse]
    total: int
