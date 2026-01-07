"""Authentication schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Login response schema."""

    message: str
    username: str


class SetupRequest(BaseModel):
    """Initial setup request schema."""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(BaseModel):
    """User response schema."""

    id: str
    username: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AuthStatusResponse(BaseModel):
    """Auth status response schema."""

    setup_required: bool
    authenticated: bool
    user: Optional[UserResponse] = None
