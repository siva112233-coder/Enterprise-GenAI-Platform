"""
FastAPI application entrypoint for the LangGraph agent service.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from shared.config import BaseServiceSettings
from shared.models import HealthResponse
from shared.utils import setup_basic_logger

logger = setup_basic_logger("langgraph-service")
settings = BaseServiceSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events handler."""
    logger.info("Starting LangGraph agent service...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("Shutting down LangGraph agent service...")


app = FastAPI(
    title="LangGraph Agent Service",
    version="0.1.0",
    description="Enterprise-grade LangGraph agentic workflow orchestrator",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check endpoint."""
    return HealthResponse(status="healthy", service="langgraph-service")
