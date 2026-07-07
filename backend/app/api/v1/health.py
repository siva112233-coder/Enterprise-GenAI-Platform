"""
Health check endpoint for the Enterprise GenAI Platform.

Provides the GET /health route as specified in Module 1A.

Future endpoints will be added as separate router modules under
``app/api/v1/`` and registered in ``app/api/v1/__init__.py``.
"""

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """
    Schema for the health check response.

    Attributes:
        status: Current health status of the service.
        service: Identifier of the service responding.
    """

    status: str
    service: str

    model_config = {"json_schema_extra": {"example": {"status": "healthy", "service": "backend"}}}


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description=(
        "Returns the current operational status of the backend service. "
        "Suitable for use with load balancer health probes, container "
        "orchestrator liveness/readiness checks (Kubernetes, ECS, etc.), "
        "and uptime monitoring systems."
    ),
    responses={
        200: {
            "description": "Service is healthy and accepting requests.",
            "content": {
                "application/json": {
                    "example": {"status": "healthy", "service": "backend"}
                }
            },
        }
    },
)
async def health_check() -> HealthResponse:
    """
    Liveness probe endpoint.

    Returns a fixed ``{"status": "healthy", "service": "backend"}`` response
    when the application process is running and able to handle requests.

    Note: This is a *liveness* check only. It does NOT verify downstream
    dependencies (database, cache, external APIs). A separate readiness
    endpoint verifying downstream connectivity will be added in a future module.

    Returns:
        HealthResponse: JSON payload confirming service health.
    """
    settings = get_settings()
    logger.debug("Health check requested", service=settings.APP_NAME)
    return HealthResponse(status="healthy", service="backend")
