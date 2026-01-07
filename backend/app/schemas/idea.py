"""Idea schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator

from app.models.idea import TradeType, PairOrientation, IdeaStatus, Horizon


class IdeaCreate(BaseModel):
    """Schema for creating an idea."""

    folder_id: str
    title: str = Field(..., min_length=1, max_length=255)
    trade_type: TradeType
    pair_orientation: Optional[PairOrientation] = None
    start_date: date
    entry_price_primary: Decimal = Field(..., gt=0)
    entry_price_secondary: Optional[Decimal] = Field(None, gt=0)
    position_size: Decimal = Field(default=Decimal("0"), ge=0)
    horizon: Horizon = Horizon.OTHER
    thesis_md: Optional[str] = None
    catalysts: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    kill_criteria_md: Optional[str] = None
    target_price_primary: Optional[Decimal] = Field(None, gt=0)
    stop_level_primary: Optional[Decimal] = Field(None, gt=0)
    target_price_secondary: Optional[Decimal] = Field(None, gt=0)
    stop_level_secondary: Optional[Decimal] = Field(None, gt=0)

    @model_validator(mode="after")
    def validate_pair_trade(self) -> "IdeaCreate":
        """Validate pair trade fields."""
        if self.trade_type == TradeType.PAIR_LONG_SHORT:
            if not self.pair_orientation:
                raise ValueError("pair_orientation is required for PAIR_LONG_SHORT trade type")
            if not self.entry_price_secondary:
                raise ValueError(
                    "entry_price_secondary is required for PAIR_LONG_SHORT trade type"
                )
        return self


class IdeaUpdate(BaseModel):
    """Schema for updating an idea."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    horizon: Optional[Horizon] = None
    thesis_md: Optional[str] = None
    catalysts: Optional[List[str]] = None
    risks: Optional[List[str]] = None
    kill_criteria_md: Optional[str] = None
    target_price_primary: Optional[Decimal] = Field(None, gt=0)
    stop_level_primary: Optional[Decimal] = Field(None, gt=0)
    target_price_secondary: Optional[Decimal] = Field(None, gt=0)
    stop_level_secondary: Optional[Decimal] = Field(None, gt=0)
    position_size: Optional[Decimal] = Field(None, ge=0)


class IdeaStatusUpdate(BaseModel):
    """Schema for updating idea status."""

    status: IdeaStatus


class CloseIdeaRequest(BaseModel):
    """Schema for closing an idea (CLOSED or KILLED status)."""

    status: IdeaStatus = Field(..., description="Must be CLOSED or KILLED")
    exit_price_primary: Decimal = Field(..., gt=0)
    exit_price_secondary: Optional[Decimal] = Field(None, gt=0)
    exit_date: date
    postmortem_note: Optional[str] = None

    @model_validator(mode="after")
    def validate_status(self) -> "CloseIdeaRequest":
        """Ensure status is CLOSED or KILLED."""
        if self.status not in (IdeaStatus.CLOSED, IdeaStatus.KILLED):
            raise ValueError("Status must be CLOSED or KILLED when closing an idea")
        return self


class IdeaResponse(BaseModel):
    """Schema for idea response."""

    id: str
    folder_id: str
    title: str
    trade_type: TradeType
    pair_orientation: Optional[PairOrientation] = None
    status: IdeaStatus
    start_date: date
    entry_price_primary: Decimal
    entry_price_secondary: Optional[Decimal] = None
    position_size: Decimal
    horizon: Horizon
    thesis_md: Optional[str] = None
    catalysts: List[str]
    risks: List[str]
    kill_criteria_md: Optional[str] = None
    target_price_primary: Optional[Decimal] = None
    stop_level_primary: Optional[Decimal] = None
    target_price_secondary: Optional[Decimal] = None
    stop_level_secondary: Optional[Decimal] = None
    exit_price_primary: Optional[Decimal] = None
    exit_price_secondary: Optional[Decimal] = None
    exit_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    # Computed fields (optional, populated by service)
    current_price_primary: Optional[Decimal] = None
    current_price_secondary: Optional[Decimal] = None
    pnl_percent: Optional[Decimal] = None
    pnl_absolute: Optional[Decimal] = None
    folder_name: Optional[str] = None

    model_config = {"from_attributes": True}


class IdeaListResponse(BaseModel):
    """Schema for idea list response."""

    ideas: List[IdeaResponse]
    total: int
