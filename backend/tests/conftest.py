"""Pytest configuration and fixtures."""

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.dependencies import get_current_user
from app.main import app
from app.models.user import User
from app.services.auth_service import AuthService


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(db: Session) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        password_hash=AuthService.hash_password("testpassword"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def client(db: Session, test_user: User) -> TestClient:
    """Create a test client with database and auth overrides."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_folder_data():
    """Sample folder creation data."""
    return {
        "type": "SINGLE",
        "ticker_primary": "AAPL",
        "description": "Apple Inc.",
        "tags": ["tech", "large-cap"],
    }


@pytest.fixture
def sample_pair_folder_data():
    """Sample pair folder creation data."""
    return {
        "type": "PAIR",
        "ticker_primary": "AAPL",
        "ticker_secondary": "MSFT",
        "description": "Apple vs Microsoft",
        "tags": ["pairs"],
    }
