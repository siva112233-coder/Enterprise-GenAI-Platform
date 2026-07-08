"""
GET /api/v1/health — Gateway health check endpoint.
"""

from __future__ import annotations

from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, status

from app.core.config import GatewaySettings
from app.core.dependencies import get_provider_router, get_settings
from app.router.provider_router import ProviderRouter
from app.schemas.chat import ProviderStatus

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Gateway health check",
    description=(
        "Returns the overall health of the AI Gateway and the status of "
        "each registered provider.  Suitable for use as a Kubernetes "
        "readiness probe or load-balancer health check."
    ),
)
async def health_check(
    provider_router: Annotated[ProviderRouter, Depends(get_provider_router)],
    settings: Annotated[GatewaySettings, Depends(get_settings)],
) -> Dict[str, Any]:
    """
    Report gateway and per-provider health.

    The gateway is considered **healthy** if it is running and at least one
    provider reports ``healthy`` or ``degraded``.

    **Example response**:
    ```json
    {
        "status": "healthy",
        "service": "ai-gateway",
        "version": "1.0.0",
        "environment": "development",
        "providers": {
            "openai":   "healthy",
            "claude":   "unconfigured",
            "gemini":   "unconfigured",
            "deepseek": "unconfigured",
            "groq":     "unconfigured",
            "ollama":   "healthy"
        }
    }
    ```
    """
    provider_statuses: Dict[str, str] = {}

    for name in provider_router.list_provider_names():
        provider = provider_router.get(name)
        try:
            status_val = await provider.health()
            provider_statuses[name] = status_val.value if hasattr(status_val, "value") else str(status_val)
        except Exception:
            provider_statuses[name] = ProviderStatus.UNAVAILABLE.value

    # Gateway is healthy if it is running — individual providers have their own status
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "environment": settings.ENVIRONMENT,
        "providers": provider_statuses,
    }
