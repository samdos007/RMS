"""FastAPI dependencies for authentication and database access."""

from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService


async def get_current_user(
    db: Session = Depends(get_db),
    rms_session: Optional[str] = Cookie(None),
) -> User:
    """
    Dependency that returns the current authenticated user.

    Raises HTTPException 401 if not authenticated.
    """
    if not rms_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    auth_service = AuthService(db)
    user = auth_service.verify_session(rms_session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    return user


async def get_optional_user(
    db: Session = Depends(get_db),
    rms_session: Optional[str] = Cookie(None),
) -> Optional[User]:
    """
    Dependency that returns the current user if authenticated, None otherwise.

    Does not raise an exception if not authenticated.
    """
    if not rms_session:
        return None

    auth_service = AuthService(db)
    return auth_service.verify_session(rms_session)
