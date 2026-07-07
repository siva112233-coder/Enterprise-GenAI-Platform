"""
Database session dependency for FastAPI request handlers.

Provides the ``get_db`` async generator that yields a per-request
``AsyncSession`` with automatic commit/rollback/close lifecycle management.

This module is intentionally thin — it exists solely as the bridge between
the session factory (``app.db.database``) and the FastAPI dependency system.
All business logic lives in repositories and services.

Usage in a route handler::

    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import get_db

    @router.get("/example")
    async def example_route(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(MyModel))
        ...
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.database import get_session_factory

logger = get_logger(__name__)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a transactional database session.

    Lifecycle per request:
    1. Acquire a session from the connection pool.
    2. Yield it to the route handler.
    3. On success: commit the transaction.
    4. On exception: rollback the transaction and re-raise.
    5. Always: close the session and return the connection to the pool.

    The explicit try/except/finally pattern ensures the session is always
    properly cleaned up, even if an unexpected exception propagates.

    Yields:
        AsyncSession: A SQLAlchemy async session bound to a transaction.

    Raises:
        Exception: Re-raises any exception that occurs during request handling
                   after performing a transaction rollback.
    """
    session_factory = get_session_factory()

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            logger.warning(
                "Rolling back database session due to exception",
                exc_type=type(exc).__name__,
                exc_msg=str(exc),
            )
            await session.rollback()
            raise
