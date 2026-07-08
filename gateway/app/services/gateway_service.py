"""
GatewayService — orchestration layer for LLM requests.

Responsibilities:
  - Receive a validated ``ChatRequest``
  - Resolve and validate the target provider
  - Delegate the call to the provider
  - Measure wall-clock latency
  - Return a structured ``ChatResponse``

Explicitly NOT responsible for:
  - Storing telemetry
  - Logging costs
  - Calling LangGraph
  - Authentication
  - Persistent state of any kind
"""

from __future__ import annotations

import time
from typing import AsyncIterator

from app.core.logging import get_logger
from app.exceptions.gateway import InvalidModel, ProviderUnavailable
from app.providers.base import LLMProvider
from app.router.provider_router import ProviderRouter
from app.schemas.chat import ChatRequest, ChatResponse, ProviderStatus

logger = get_logger(__name__)


class GatewayService:
    """
    Stateless orchestration service for the AI Gateway.

    Injected with a ``ProviderRouter`` — all routing decisions are
    delegated to the router, keeping this service focused on the
    request lifecycle.

    Args:
        provider_router: Populated ``ProviderRouter`` singleton
                         (injected via FastAPI's ``Depends``).
    """

    def __init__(self, provider_router: ProviderRouter) -> None:
        self._router = provider_router

    # ── Public interface ──────────────────────────────────────────────────────

    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process a non-streaming chat request end-to-end.

        Flow:
        1. Resolve provider from router (raises ``ProviderNotFound`` if missing)
        2. Assert provider is not UNAVAILABLE (raises ``ProviderUnavailable``)
        3. Validate model is in the provider's supported list
        4. Delegate to ``provider.chat()``
        5. Return ``ChatResponse`` with latency

        Args:
            request: Validated ``ChatRequest`` from the API layer.

        Returns:
            Populated ``ChatResponse``.

        Raises:
            ProviderNotFound:    Unknown provider slug.
            ProviderUnavailable: Provider health check failed.
            InvalidModel:        Model not in provider's catalogue.
        """
        provider = await self._resolve_provider(request)

        logger.info(
            "gateway.chat.start",
            provider=request.provider,
            model=request.model,
            message_count=len(request.messages),
        )

        start_ms = time.perf_counter() * 1_000

        response = await provider.chat(
            model=request.model,
            messages=request.messages,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens,
        )

        latency_ms = (time.perf_counter() * 1_000) - start_ms

        # Overwrite latency with the gateway-measured value for consistency
        response = ChatResponse(
            request_id=response.request_id,
            provider=response.provider,
            model=response.model,
            response=response.response,
            usage=response.usage,
            latency_ms=round(latency_ms, 2),
            finish_reason=response.finish_reason,
        )

        logger.info(
            "gateway.chat.complete",
            provider=request.provider,
            model=request.model,
            latency_ms=response.latency_ms,
        )

        return response

    async def stream_chat(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[str]:
        """
        Process a streaming chat request, yielding text deltas.

        The caller (endpoint handler) is responsible for wrapping
        each delta into the appropriate SSE or chunked-transfer format.

        Args:
            request: Validated ``ChatRequest`` with ``stream=True``.

        Yields:
            str — incremental response text from the provider.

        Raises:
            ProviderNotFound:    Unknown provider slug.
            ProviderUnavailable: Provider health check failed.
            InvalidModel:        Model not in provider's catalogue.
        """
        provider = await self._resolve_provider(request)

        logger.info(
            "gateway.stream.start",
            provider=request.provider,
            model=request.model,
        )

        async for chunk in provider.stream(
            model=request.model,
            messages=request.messages,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens,
        ):
            yield chunk

        logger.info(
            "gateway.stream.complete",
            provider=request.provider,
            model=request.model,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    async def _resolve_provider(self, request: ChatRequest) -> LLMProvider:
        """
        Retrieve and validate the target provider for ``request``.

        Raises:
            ProviderNotFound:    If the provider slug is not registered.
            ProviderUnavailable: If the provider's health status is UNAVAILABLE.
            InvalidModel:        If the model is not in the provider's catalogue.
        """
        # 1. Resolve (raises ProviderNotFound if missing)
        provider = self._router.get(request.provider)

        # 2. Health gate (raises ProviderUnavailable if down)
        status = await provider.health()
        if status == ProviderStatus.UNAVAILABLE:
            raise ProviderUnavailable(
                provider=request.provider,
                reason="Health check returned UNAVAILABLE.",
            )

        # 3. Model validation — compare against the provider's catalogue
        try:
            supported_models = await provider.list_models()
            supported_ids = {m.id for m in supported_models}
            if supported_ids and request.model not in supported_ids:
                raise InvalidModel(
                    provider=request.provider,
                    model=request.model,
                )
        except InvalidModel:
            raise
        except Exception:
            # If model listing fails for any other reason, proceed optimistically.
            # The provider itself will reject unsupported models.
            logger.warning(
                "gateway.model_validation.skipped",
                provider=request.provider,
                model=request.model,
                reason="list_models() raised an unexpected error.",
            )

        return provider
