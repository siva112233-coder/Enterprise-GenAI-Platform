"""
AI Gateway — FastAPI application entry point.

Module 3A: Enterprise AI Gateway
Single entry point for all LLM provider requests.

Startup sequence:
  1. Configure structured logging
  2. Build provider router (registers all providers)
  3. Mount middleware (error handling, request logging, CORS)
  4. Include versioned API router
  5. Expose OpenAPI docs

The gateway exposes:
  POST  /api/v1/chat        — LLM chat completion
  GET   /api/v1/providers   — List registered providers
  GET   /api/v1/models      — List supported models
  GET   /api/v1/health      — Gateway health check
  GET   /health             — Lightweight liveness probe (for Docker/K8s)
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.dependencies import _build_provider_router
from app.core.logging import configure_logging, get_logger
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.logging_middleware import RequestLoggingMiddleware


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    ASGI lifespan handler.

    Runs startup logic before the first request and teardown after the last.
    """
    # 1. Configure structured logging (must be first)
    configure_logging()
    logger = get_logger("gateway.startup")

    logger.info(
        "gateway.starting",
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        environment=settings.ENVIRONMENT,
        api_prefix=settings.API_PREFIX,
    )

    # 2. Pre-warm the provider router singleton (validates config at startup)
    provider_router = _build_provider_router()
    logger.info(
        "gateway.providers_registered",
        count=len(provider_router),
        providers=provider_router.list_provider_names(),
    )

    yield  # ← application serves requests here

    # Teardown
    logger.info("gateway.shutdown", service=settings.SERVICE_NAME)


# ─────────────────────────────────────────────────────────────────────────────
# Application factory
# ─────────────────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """
    Construct and configure the FastAPI application.

    Returns:
        A fully configured ``FastAPI`` instance.
    """
    application = FastAPI(
        title="Enterprise AI Gateway",
        version=settings.SERVICE_VERSION,
        description=(
            "**Enterprise AI Gateway** — the single entry point for all LLM requests.\n\n"
            "Routes requests to the appropriate provider "
            "(OpenAI, Claude, Gemini, DeepSeek, Groq, Ollama) "
            "and returns a structured response.\n\n"
            "**Module 3A** of the Enterprise GenAI Platform."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        contact={
            "name": "Enterprise GenAI Platform",
            "url": "https://github.com/your-org/enterprise-genai-platform",
        },
        license_info={
            "name": "Proprietary",
        },
    )

    # ── Middleware (outermost first — applied inside-out) ─────────────────────
    # CORS must be outermost so pre-flight requests are handled before auth
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Error handler wraps the request logger so exceptions are caught after logging
    application.add_middleware(ErrorHandlerMiddleware)
    # Request logger is innermost — logs every request/response pair
    application.add_middleware(RequestLoggingMiddleware)

    # ── Versioned API routes ──────────────────────────────────────────────────
    application.include_router(api_v1_router, prefix=settings.API_PREFIX)

    # ── Liveness probe (for Docker HEALTHCHECK / K8s liveness) ───────────────
    @application.get(
        "/health",
        tags=["Health"],
        summary="Liveness probe",
        description="Lightweight liveness check — returns 200 if the process is alive.",
        include_in_schema=False,
    )
    async def liveness() -> dict:
        return {
            "status": "alive",
            "service": settings.SERVICE_NAME,
            "version": settings.SERVICE_VERSION,
        }

    return application


# ─────────────────────────────────────────────────────────────────────────────
# Application instance (imported by uvicorn)
# ─────────────────────────────────────────────────────────────────────────────

app = create_app()
