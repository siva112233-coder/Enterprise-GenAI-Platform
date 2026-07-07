"""
FastAPI application factory for the Enterprise GenAI Platform — Module 1A.

Architecture overview:
- Async-first: all I/O operations (DB, HTTP) use async/await
- Lifespan context manager: deterministic startup/shutdown ordering
- Layered middleware: logging → CORS → routing
- OpenAPI docs enabled only in non-production environments
- Health check at GET /health (no auth required)

Startup sequence:
    1. setup_logging()          — configure structlog
    2. init_db()                — create engine + session factory
    3. register middleware       — CORS, request logging
    4. mount routers            — /api/v1/*

Shutdown sequence:
    1. close_db()               — dispose connection pool
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.db.database import close_db, init_db
from app.middleware.logging import RequestLoggingMiddleware

# ---------------------------------------------------------------------------
# Logging must be configured before any other module emits log records
# ---------------------------------------------------------------------------
setup_logging()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Lifespan handler
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application startup and shutdown lifecycle.

    FastAPI's lifespan context manager replaces the deprecated
    ``@app.on_event("startup")`` / ``@app.on_event("shutdown")`` pattern.

    Startup:
        - Initialise the database engine and session factory.
        - Log the application start event with key metadata.

    Shutdown:
        - Dispose the database connection pool.
        - Log the graceful shutdown event.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control is yielded to the application request loop.
    """
    settings = get_settings()

    # --- Startup ---
    logger.info(
        "Starting Enterprise GenAI Platform",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        api_prefix=settings.API_V1_PREFIX,
    )

    init_db()
    logger.info("Database initialised successfully.")

    yield  # Application is running — handle requests

    # --- Shutdown ---
    logger.info("Shutting down Enterprise GenAI Platform — releasing resources.")
    await close_db()
    logger.info("Database connection pool disposed. Shutdown complete.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_application() -> FastAPI:
    """
    Construct and configure the FastAPI application instance.

    Separating construction into a factory function enables:
    - Clean unit testing (instantiate a fresh app per test)
    - Integration testing with dependency overrides
    - Future support for multiple ASGI app variants

    Returns:
        FastAPI: The fully configured application instance.
    """
    settings = get_settings()

    # Disable interactive docs in production to reduce attack surface
    docs_url = "/docs" if not settings.is_production else None
    redoc_url = "/redoc" if not settings.is_production else None
    openapi_url = "/openapi.json" if not settings.is_production else None

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=lifespan,
        # Global response class — consistent JSON serialisation
        default_response_class=JSONResponse,
    )

    # -----------------------------------------------------------------------
    # Middleware registration (order matters — outermost runs first)
    # -----------------------------------------------------------------------
    # 1. Request logging (outermost — captures all requests including CORS preflight)
    application.add_middleware(RequestLoggingMiddleware)

    # 2. CORS (must be after logging to avoid double-logging preflight)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # -----------------------------------------------------------------------
    # Router registration
    # -----------------------------------------------------------------------
    application.include_router(
        api_router,
        prefix=settings.API_V1_PREFIX,
    )

    return application


# ---------------------------------------------------------------------------
# ASGI application entry point
# ---------------------------------------------------------------------------
app: FastAPI = create_application()
