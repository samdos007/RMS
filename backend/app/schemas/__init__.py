"""Pydantic schemas for API request/response validation."""

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    SetupRequest,
    ChangePasswordRequest,
    UserResponse,
    AuthStatusResponse,
)
from app.schemas.folder import (
    FolderCreate,
    FolderUpdate,
    FolderResponse,
    FolderListResponse,
    ThemeTickerPerformance,
)
from app.schemas.idea import (
    IdeaCreate,
    IdeaUpdate,
    IdeaResponse,
    IdeaListResponse,
    IdeaStatusUpdate,
    CloseIdeaRequest,
)
from app.schemas.note import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
)
from app.schemas.attachment import (
    AttachmentResponse,
)
from app.schemas.price_snapshot import (
    PriceSnapshotCreate,
    PriceSnapshotResponse,
    BackfillRequest,
    BackfillResponse,
)
from app.schemas.earnings import (
    EarningsCreate,
    EarningsUpdate,
    EarningsResponse,
)
from app.schemas.guidance import (
    GuidanceCreate,
    GuidanceUpdate,
    GuidanceResponse,
    GuidanceListResponse,
)
from app.schemas.pnl import (
    PnLResponse,
    PnLHistoryResponse,
)

__all__ = [
    # Auth
    "LoginRequest",
    "LoginResponse",
    "SetupRequest",
    "ChangePasswordRequest",
    "UserResponse",
    "AuthStatusResponse",
    # Folder
    "FolderCreate",
    "FolderUpdate",
    "FolderResponse",
    "FolderListResponse",
    "ThemeTickerPerformance",
    # Idea
    "IdeaCreate",
    "IdeaUpdate",
    "IdeaResponse",
    "IdeaListResponse",
    "IdeaStatusUpdate",
    "CloseIdeaRequest",
    # Note
    "NoteCreate",
    "NoteUpdate",
    "NoteResponse",
    # Attachment
    "AttachmentResponse",
    # PriceSnapshot
    "PriceSnapshotCreate",
    "PriceSnapshotResponse",
    "BackfillRequest",
    "BackfillResponse",
    # Earnings
    "EarningsCreate",
    "EarningsUpdate",
    "EarningsResponse",
    # Guidance
    "GuidanceCreate",
    "GuidanceUpdate",
    "GuidanceResponse",
    "GuidanceListResponse",
    # PnL
    "PnLResponse",
    "PnLHistoryResponse",
]
