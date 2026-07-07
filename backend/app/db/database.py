"""
Async SQLAlchemy engine and session factory for the Enterprise GenAI Platform.

Architecture decisions:
- AsyncEngine + AsyncSession for non-blocking I/O (FastAPI async handlers)
- NullPool in testing to prevent connection bleed between test cases
- Singleton engine — created once at startup, shared across all requests
- Sessions are NOT shared; each request gets its own via ``get_db`` dependency
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Module-level engine and session factory (singletons)
# ---------------------------------------------------------------------------
# These are initialized lazily on first import via ``init_db`` called in the
# application lifespan handler. Direct access before initialization will raise.
_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def create_engine() -> AsyncEngine:
    """
    Create and return a configured AsyncEngine instance.

    Connection pool settings are tuned for a production workload:
    - pool_size:     Persistent connections kept alive between requests.
    - max_overflow:  Extra connections allowed during traffic spikes.
    - pool_timeout:  Seconds to wait for a connection before raising.
    - pool_recycle:  Recycle connections older than N seconds (avoids
                     stale connections dropped by the DB server or firewall).
    - pool_pre_ping: Issue a lightweight SELECT 1 before handing a
                     connection to a request (detects dropped connections).

    Returns:
        AsyncEngine: A configured SQLAlchemy async engine.
    """
    settings = get_settings()
    db_url = str(settings.DATABASE_URL)

    logger.info(
        "Creating database engine",
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )

    engine = create_async_engine(
        db_url,
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True,
    )

    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Create and return an async session factory bound to the given engine.

    Sessions are configured with:
    - autocommit=False: Explicit transaction management (best practice).
    - autoflush=False:  Prevent implicit flushes that can hide bugs.
    - expire_on_commit=False: Keep objects usable after commit without
                              triggering lazy-load on attribute access.

    Args:
        engine: The AsyncEngine instance to bind sessions to.

    Returns:
        async_sessionmaker: A factory that produces AsyncSession instances.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


def init_db() -> None:
    """
    Initialize the module-level engine and session factory.

    Must be called once during application startup (in the lifespan handler).
    Calling multiple times is safe — subsequent calls are no-ops.
    """
    global _engine, _async_session_factory

    if _engine is not None:
        logger.debug("Database engine already initialized — skipping.")
        return

    _engine = create_engine()
    _async_session_factory = create_session_factory(_engine)
    logger.info("Database engine and session factory initialized successfully.")


async def close_db() -> None:
    """
    Gracefully dispose of the engine connection pool.

    Must be called during application shutdown (in the lifespan handler)
    to ensure all connections are released cleanly and no connection leaks
    occur in containerized or serverless environments.
    """
    global _engine, _async_session_factory

    if _engine is not None:
        logger.info("Disposing database engine connection pool.")
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
        logger.info("Database connection pool disposed.")


def get_engine() -> AsyncEngine:
    """
    Return the initialized engine instance.

    Raises:
        RuntimeError: If ``init_db()`` has not been called yet.
    """
    if _engine is None:
        raise RuntimeError(
            "Database engine not initialized. "
            "Ensure ``init_db()`` is called in the application lifespan handler."
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Return the initialized session factory.

    Raises:
        RuntimeError: If ``init_db()`` has not been called yet.
    """
    if _async_session_factory is None:
        raise RuntimeError(
            "Session factory not initialized. "
            "Ensure ``init_db()`` is called in the application lifespan handler."
        )
    return _async_session_factory
