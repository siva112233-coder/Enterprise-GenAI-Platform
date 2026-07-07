"""
FastAPI application entrypoint for the AI Gateway.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from shared.config import BaseServiceSettings
from shared.models import HealthResponse
from shared.utils import setup_basic_logger

logger = setup_basic_logger("gateway")
settings = BaseServiceSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events handler."""
    logger.info("Starting AI Gateway...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("Shutting down AI Gateway...")


app = FastAPI(
    title="AI Gateway",
    version="0.1.0",
    description="Enterprise-grade LLM Gateway",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check endpoint."""
    return HealthResponse(status="healthy", service="gateway")
