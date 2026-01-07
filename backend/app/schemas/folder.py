"""Folder schemas."""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.folder import FolderType


class TickerPnL(BaseModel):
    """Schema for ticker with P&L in a theme."""

    ticker: str = Field(..., min_length=1, max_length=20)
    pnl: Optional[Decimal] = None


class FolderCreate(BaseModel):
    """Schema for creating a folder."""

    type: FolderType = FolderType.SINGLE

    # SINGLE/PAIR fields (conditional)
    ticker_primary: Optional[str] = Field(None, max_length=20)
    ticker_secondary: Optional[str] = Field(None, max_length=20)

    # THEME fields (conditional)
    theme_name: Optional[str] = Field(None, min_length=1, max_length=100)
    theme_date: Optional[date] = None
    theme_thesis: Optional[str] = None
    theme_tickers: List[TickerPnL] = Field(default_factory=list)

    # Common fields
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_folder_type(self) -> "FolderCreate":
        """Ensure correct fields for each folder type."""
        if self.type == FolderType.SINGLE:
            if not self.ticker_primary:
                raise ValueError("ticker_primary is required for SINGLE type")
            if self.theme_name:
                raise ValueError("theme_name not allowed for SINGLE type")

        elif self.type == FolderType.PAIR:
            if not self.ticker_primary or not self.ticker_secondary:
                raise ValueError("Both ticker_primary and ticker_secondary are required for PAIR type")
            if self.theme_name:
                raise ValueError("theme_name not allowed for PAIR type")

        elif self.type == FolderType.THEME:
            if not self.theme_name:
                raise ValueError("theme_name is required for THEME type")
            if self.ticker_primary or self.ticker_secondary:
                raise ValueError("Individual tickers not allowed for THEME type")

        return self


class FolderUpdate(BaseModel):
    """Schema for updating a folder."""

    description: Optional[str] = None
    tags: Optional[List[str]] = None

    # THEME-specific updates
    theme_date: Optional[date] = None
    theme_thesis: Optional[str] = None
    theme_tickers: Optional[List[TickerPnL]] = None


class ThemeOption(BaseModel):
    """Schema for theme autocomplete option."""

    id: str
    name: str
    date: Optional[date] = None
    ticker_count: int


class ThemeTickerPerformance(BaseModel):
    """Schema for individual ticker performance in a theme."""

    ticker: str
    start_price: Optional[float] = None
    current_price: Optional[float] = None
    pnl_percent: Optional[float] = None


class FolderResponse(BaseModel):
    """Schema for folder response."""

    id: str
    type: FolderType

    # SINGLE/PAIR fields
    ticker_primary: Optional[str] = None
    ticker_secondary: Optional[str] = None

    # THEME fields
    theme_name: Optional[str] = None
    theme_date: Optional[date] = None
    theme_thesis: Optional[str] = None
    theme_tickers: List[TickerPnL] = Field(default_factory=list)

    # Theme associations
    theme_ids: List[str] = Field(default_factory=list)

    # Computed/common fields
    name: str
    description: Optional[str] = None
    tags: List[str]
    tickers: List[str]
    created_at: datetime
    updated_at: datetime
    idea_count: int = 0
    active_idea_count: int = 0

    model_config = {"from_attributes": True}


class FolderListResponse(BaseModel):
    """Schema for folder list response."""

    folders: List[FolderResponse]
    total: int
