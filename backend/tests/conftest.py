"""
Pytest configuration and shared fixtures for the Enterprise GenAI Platform.

This conftest.py is the root fixture provider for the entire test suite.
It configures:
- asyncio mode for async tests (pytest-asyncio)
- Test application client with dependency overrides
- In-memory or test-database session fixtures
- Settings overrides for test isolation

Architecture decisions:
- Use httpx.AsyncClient as the test client (same as production path)
- Override get_db with a test session that rolls back after each test
- Override get_settings with test-specific configuration
- Tests are fully isolated: each test gets a clean database state
"""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_application

# ---------------------------------------------------------------------------
# Test settings override
# ---------------------------------------------------------------------------
# Use a separate test database to isolate tests from the development database.
# For CI environments, this can be overridden via environment variables.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def get_test_settings() -> Settings:
    """
    Return Settings configured for the test environment.

    Overrides the production settings singleton to use:
    - ENVIRONMENT=testing (disables production safety checks)
    - DEBUG=True (more verbose output in test failures)
    """
    return Settings(
        ENVIRONMENT="testing",
        DEBUG=True,
        LOG_LEVEL="WARNING",  # Suppress verbose logs in test output
        LOG_FORMAT="text",
        SECRET_KEY="test-secret-key-not-for-production",
        # DB settings are overridden at the engine level in fixtures below
        POSTGRES_HOST="localhost",
        POSTGRES_USER="test",
        POSTGRES_PASSWORD="test",
        POSTGRES_DB="test_db",
    )


# ---------------------------------------------------------------------------
# Async event loop
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def event_loop_policy():
    """
    Use the default asyncio event loop policy for the full test session.

    pytest-asyncio 0.24+ deprecates overriding ``event_loop`` directly.
    Returning a policy here (or None for the platform default) is the
    recommended replacement when you need session-scoped async fixtures.
    """
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """
    Create a test database engine for the full test session.

    Uses SQLite in-memory database for speed and isolation.
    NullPool prevents connection sharing between tests.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )

    # Create all tables defined on Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after the session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
def test_session_factory(test_engine):
    """Return an async_sessionmaker bound to the test engine."""
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def db_session(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a test database session that rolls back after each test.

    Using a savepoint (SAVEPOINT + ROLLBACK TO SAVEPOINT) ensures that:
    - Each test starts with a clean database state
    - Tests do not interfere with each other
    - No data persists between tests (full isolation)
    """
    async with test_session_factory() as session:
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# FastAPI application and client fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def test_app(test_session_factory):
    """
    Create a FastAPI application instance with test dependency overrides.

    Overrides:
    - get_db: Replaced with test session that rolls back after each test
    - get_settings: Replaced with test-specific settings
    """
    application = create_application()

    # Override database dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_factory() as session:
            yield session

    # Override settings dependency
    application.dependency_overrides[get_settings] = get_test_settings
    application.dependency_overrides[get_db] = override_get_db

    return application


@pytest_asyncio.fixture
async def client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP test client for making requests to the test app.

    Uses ASGITransport to send requests directly to the ASGI app without
    a live server, making tests faster and more deterministic.
    """
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://testserver",
    ) as ac:
        yield ac
