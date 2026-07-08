"""
GET /api/v1/models — List all supported models across providers.
"""

from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_provider_router
from app.router.provider_router import ProviderRouter
from app.schemas.chat import ModelsResponse

router = APIRouter(tags=["Models"])


@router.get(
    "/models",
    response_model=ModelsResponse,
    status_code=status.HTTP_200_OK,
    summary="List all supported models",
    description=(
        "Returns the combined model catalogue across all registered providers. "
        "Optionally filter by provider name using the ``provider`` query parameter."
    ),
)
async def list_models(
    provider_router: Annotated[ProviderRouter, Depends(get_provider_router)],
    provider: Optional[str] = Query(
        default=None,
        description="Filter by provider slug (e.g. openai, claude, gemini).",
        example="openai",
    ),
) -> ModelsResponse:
    """
    Return the full model catalogue, optionally filtered by provider.

    **Usage**:
    - ``GET /api/v1/models`` — all models from all providers
    - ``GET /api/v1/models?provider=openai`` — OpenAI models only

    **Example response**:
    ```json
    {
        "models": [
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "context_window": 128000,
                "supports_streaming": true,
                "supports_system_prompt": true
            },
            ...
        ],
        "total": 25
    }
    ```
    """
    if provider:
        # Single-provider model list
        p = provider_router.get(provider.strip().lower())  # raises ProviderNotFound
        models = await p.list_models()
    else:
        models = await provider_router.list_all_models()

    return ModelsResponse(models=models, total=len(models))
