"""Application configuration using Pydantic Settings."""

import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Investment RMS"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "change-this-to-a-secure-random-string-at-least-32-chars"
    COOKIE_SECURE: bool = False  # Set True in production with HTTPS
    SESSION_MAX_AGE: int = 60 * 60 * 24 * 7  # 7 days in seconds

    # Database
    DATA_DIR: Path = Path("./data")
    DATABASE_URL: str = ""

    # File uploads
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".xlsx", ".xls", ".csv",  # Spreadsheets
        ".pdf",  # Documents
        ".png", ".jpg", ".jpeg", ".gif",  # Images
        ".txt", ".md",  # Text files
    ]

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Railway-specific configuration
    PORT: int = int(os.getenv("PORT", "8000"))  # Railway sets PORT

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from environment."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        # Railway may pass as comma-separated string
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return ["http://localhost:5173"]

    @property
    def database_url(self) -> str:
        """Get database URL, defaulting to SQLite in data directory."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        db_path = self.DATA_DIR / "rms.db"
        return f"sqlite:///{db_path}"

    @property
    def upload_dir(self) -> Path:
        """Get upload directory path."""
        return self.DATA_DIR / "uploads"

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
