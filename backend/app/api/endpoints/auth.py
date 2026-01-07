"""Authentication endpoints."""

from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    AuthStatusResponse,
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    SetupRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status(
    db: Session = Depends(get_db),
    rms_session: Optional[str] = Cookie(None),
) -> AuthStatusResponse:
    """
    Check authentication status.

    Returns whether setup is required and if the user is authenticated.
    """
    auth_service = AuthService(db)
    setup_required = auth_service.is_setup_required()

    if not rms_session:
        return AuthStatusResponse(
            setup_required=setup_required,
            authenticated=False,
        )

    user = auth_service.verify_session(rms_session)
    if user:
        return AuthStatusResponse(
            setup_required=False,
            authenticated=True,
            user=UserResponse.model_validate(user),
        )

    return AuthStatusResponse(
        setup_required=setup_required,
        authenticated=False,
    )


@router.post("/setup", response_model=LoginResponse)
async def setup(
    request: SetupRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    Initial user setup.

    Creates the first user account. Only works when no users exist.
    """
    auth_service = AuthService(db)
    user = auth_service.setup_user(request.username, request.password)
    auth_service.create_session(user, response)

    return LoginResponse(
        message="Setup complete",
        username=user.username,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    Login with username and password.

    Sets a session cookie on success.
    """
    auth_service = AuthService(db)

    # Check if setup is required
    if auth_service.is_setup_required():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setup required. Use /auth/setup first.",
        )

    user = auth_service.authenticate(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    auth_service.create_session(user, response)

    return LoginResponse(
        message="Login successful",
        username=user.username,
    )


@router.post("/logout")
async def logout(
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    """
    Logout and clear session cookie.
    """
    auth_service = AuthService(db)
    auth_service.logout(response)

    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Get current authenticated user information.
    """
    return UserResponse.model_validate(current_user)


@router.post("/password")
async def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Change the current user's password.
    """
    auth_service = AuthService(db)
    auth_service.change_password(
        current_user,
        request.current_password,
        request.new_password,
    )

    return {"message": "Password changed successfully"}
