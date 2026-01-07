"""Authentication service for single-user auth."""

from datetime import datetime
from typing import Optional

import bcrypt
from fastapi import HTTPException, Response, status
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User


class AuthService:
    """
    Single-user authentication service.

    Uses bcrypt for password hashing and itsdangerous for signed session cookies.
    """

    COOKIE_NAME = "rms_session"

    def __init__(self, db: Session):
        self.db = db
        self.serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )

    def is_setup_required(self) -> bool:
        """Check if initial setup is required (no users exist)."""
        return self.db.query(User).count() == 0

    def setup_user(self, username: str, password: str) -> User:
        """
        Create the initial user during first-time setup.

        Raises HTTPException if a user already exists.
        """
        if not self.is_setup_required():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already configured. Use login instead.",
            )

        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters.",
            )

        user = User(
            username=username,
            password_hash=self.hash_password(password),
            created_at=datetime.utcnow(),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user credentials.

        Returns the user if credentials are valid, None otherwise.
        """
        user = self.db.query(User).filter(User.username == username).first()

        if user and user.is_active and self.verify_password(password, user.password_hash):
            # Update last login timestamp
            user.last_login = datetime.utcnow()
            self.db.commit()
            return user

        return None

    def create_session_token(self, user_id: str) -> str:
        """Create a signed session token."""
        data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        return self.serializer.dumps(data, salt="session")

    def verify_session_token(self, token: str) -> Optional[str]:
        """
        Verify a session token and return the user_id if valid.

        Returns None if the token is invalid or expired.
        """
        try:
            data = self.serializer.loads(
                token,
                salt="session",
                max_age=settings.SESSION_MAX_AGE,
            )
            return data.get("user_id")
        except (BadSignature, SignatureExpired):
            return None

    def create_session(self, user: User, response: Response) -> str:
        """Create a session and set the session cookie."""
        token = self.create_session_token(user.id)

        response.set_cookie(
            key=self.COOKIE_NAME,
            value=token,
            max_age=settings.SESSION_MAX_AGE,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
        )

        return token

    def verify_session(self, token: str) -> Optional[User]:
        """
        Verify a session token and return the associated user.

        Returns None if the token is invalid or the user doesn't exist.
        """
        user_id = self.verify_session_token(token)
        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and user.is_active:
                return user
        return None

    def logout(self, response: Response) -> None:
        """Clear the session cookie."""
        response.delete_cookie(key=self.COOKIE_NAME)

    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        """
        Change a user's password.

        Raises HTTPException if current password is incorrect or new password is invalid.
        """
        if not self.verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )

        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters.",
            )

        user.password_hash = self.hash_password(new_password)
        self.db.commit()
