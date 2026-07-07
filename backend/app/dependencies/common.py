"""
FastAPI dependency providers for the Enterprise GenAI Platform.

This module centralises all FastAPI ``Depends()`` callables so that:
- Dependencies are discoverable in one place
- Mock/override patterns are consistent across the codebase
- Route handlers stay lean and focused on business logic

Currently provided:
- ``get_db``: Per-request async database session (re-exported from db.session)
- ``get_settings``: Application configuration singleton

Future additions (implemented in later modules):
- ``get_current_user``: JWT-authenticated user from the Authorization header
- ``get_current_active_user``: Validated, active user guard
- ``require_admin``: Role-based access control guard
- ``get_pagination``: Common pagination query parameters
- ``get_rate_limiter``: Per-user/per-route rate limiting

Usage in route handlers::

    from fastapi import Depends
    from app.dependencies.common import get_db, get_settings

    @router.get("/example")
    async def example(
        db: AsyncSession = Depends(get_db),
        settings: Settings = Depends(get_settings),
    ):
        ...
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated

from app.core.config import Settings, get_settings as _get_settings
from app.db.session import get_db as _get_db


# ---------------------------------------------------------------------------
# Re-exported dependencies with type aliases for cleaner route signatures
# ---------------------------------------------------------------------------

async def get_db() -> AsyncSession:  # type: ignore[return]
    """
    Yield a per-request transactional database session.

    Delegates to ``app.db.session.get_db`` (async generator).
    Re-exported here so route handlers only need to import from this module.
    """
    async for session in _get_db():
        yield session


def get_settings() -> Settings:
    """
    Return the application configuration singleton.

    Cached via ``lru_cache`` in ``app.core.config`` — safe to call repeatedly.
    """
    return _get_settings()


# ---------------------------------------------------------------------------
# Annotated type aliases (PEP 593 + FastAPI pattern)
# ---------------------------------------------------------------------------
# Use these in route signatures for the most concise DI syntax:
#
#   async def my_route(db: DBSession, settings: AppSettings) -> ...:
#
DBSession = Annotated[AsyncSession, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]
