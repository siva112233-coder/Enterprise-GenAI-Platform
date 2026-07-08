"""
GET /api/v1/providers — List all registered LLM providers.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_provider_router
from app.router.provider_router import ProviderRouter
from app.schemas.chat import ProvidersResponse

router = APIRouter(tags=["Providers"])


@router.get(
    "/providers",
    response_model=ProvidersResponse,
    status_code=status.HTTP_200_OK,
    summary="List registered LLM providers",
    description=(
        "Returns all LLM providers registered in this gateway instance, "
        "including their current health status, configuration state, "
        "and supported model IDs."
    ),
)
async def list_providers(
    provider_router: Annotated[ProviderRouter, Depends(get_provider_router)],
) -> ProvidersResponse:
    """
    Return all registered providers with live health status.

    Health checks are executed concurrently, so response time is
    bounded by the slowest provider ping (or timeout).

    **Example response**:
    ```json
    {
        "providers": [
            {
                "name": "openai",
                "display_name": "OpenAI",
                "status": "healthy",
                "models": ["gpt-4o", "gpt-4o-mini", ...],
                "configured": true
            },
            ...
        ],
        "total": 6
    }
    ```
    """
    providers = await provider_router.list_providers()
    return ProvidersResponse(providers=providers, total=len(providers))
