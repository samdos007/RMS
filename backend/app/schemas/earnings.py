"""Earnings schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.earnings import PeriodType


class EarningsCreate(BaseModel):
    """Schema for creating earnings data."""

    folder_id: str
    ticker: str = Field(..., min_length=1, max_length=20)
    period_type: PeriodType = PeriodType.QUARTERLY
    period: Optional[str] = Field(None, max_length=20)
    fiscal_quarter: str = Field(..., min_length=1, max_length=20)
    period_end_date: Optional[date] = None
    # Consensus estimates
    estimate_eps: Optional[Decimal] = None
    actual_eps: Optional[Decimal] = None
    estimate_rev: Optional[Decimal] = None
    actual_rev: Optional[Decimal] = None
    estimate_ebitda: Optional[Decimal] = None
    actual_ebitda: Optional[Decimal] = None
    estimate_fcf: Optional[Decimal] = None
    actual_fcf: Optional[Decimal] = None
    # User's own estimates
    my_estimate_eps: Optional[Decimal] = None
    my_estimate_rev: Optional[Decimal] = None
    my_estimate_ebitda: Optional[Decimal] = None
    my_estimate_fcf: Optional[Decimal] = None
    notes: Optional[str] = None


class EarningsUpdate(BaseModel):
    """Schema for updating earnings data."""

    period_type: Optional[PeriodType] = None
    period: Optional[str] = None
    period_end_date: Optional[date] = None
    # Consensus estimates
    estimate_eps: Optional[Decimal] = None
    actual_eps: Optional[Decimal] = None
    estimate_rev: Optional[Decimal] = None
    actual_rev: Optional[Decimal] = None
    estimate_ebitda: Optional[Decimal] = None
    actual_ebitda: Optional[Decimal] = None
    estimate_fcf: Optional[Decimal] = None
    actual_fcf: Optional[Decimal] = None
    # User's own estimates
    my_estimate_eps: Optional[Decimal] = None
    my_estimate_rev: Optional[Decimal] = None
    my_estimate_ebitda: Optional[Decimal] = None
    my_estimate_fcf: Optional[Decimal] = None
    notes: Optional[str] = None


class EarningsResponse(BaseModel):
    """Schema for earnings response."""

    id: str
    folder_id: str
    ticker: str
    period_type: PeriodType
    period: Optional[str] = None
    fiscal_quarter: str
    period_end_date: Optional[date] = None
    # Consensus estimates
    estimate_eps: Optional[Decimal] = None
    actual_eps: Optional[Decimal] = None
    estimate_rev: Optional[Decimal] = None
    actual_rev: Optional[Decimal] = None
    estimate_ebitda: Optional[Decimal] = None
    actual_ebitda: Optional[Decimal] = None
    estimate_fcf: Optional[Decimal] = None
    actual_fcf: Optional[Decimal] = None
    # User's own estimates
    my_estimate_eps: Optional[Decimal] = None
    my_estimate_rev: Optional[Decimal] = None
    my_estimate_ebitda: Optional[Decimal] = None
    my_estimate_fcf: Optional[Decimal] = None
    # Surprise calculations
    eps_surprise: Optional[Decimal] = None
    eps_surprise_pct: Optional[Decimal] = None
    rev_surprise: Optional[Decimal] = None
    rev_surprise_pct: Optional[Decimal] = None
    ebitda_surprise_pct: Optional[Decimal] = None
    fcf_surprise_pct: Optional[Decimal] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EarningsListResponse(BaseModel):
    """Schema for earnings list response."""

    earnings: List[EarningsResponse]
    total: int


class EarningsCSVRow(BaseModel):
    """Schema for a single row in CSV import/export."""

    ticker: str
    fiscal_quarter: str
    period_end_date: Optional[str] = None
    estimate_eps: Optional[str] = None
    actual_eps: Optional[str] = None
    estimate_rev: Optional[str] = None
    actual_rev: Optional[str] = None
    notes: Optional[str] = None
