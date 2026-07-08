"""
Dependency Injection wiring for the AI Gateway.

FastAPI resolves these callables via ``Depends()``.
All shared singletons (router, service) are constructed once and
reused across requests — no global state leaks into route handlers.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import GatewaySettings, settings
from app.providers.claude_provider import ClaudeProvider
from app.providers.deepseek_provider import DeepSeekProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.groq_provider import GroqProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.router.provider_router import ProviderRouter
from app.services.gateway_service import GatewayService


@lru_cache(maxsize=1)
def get_settings() -> GatewaySettings:
    """Return the cached gateway settings singleton."""
    return settings


@lru_cache(maxsize=1)
def _build_provider_router() -> ProviderRouter:
    """
    Construct and populate the ProviderRouter singleton.

    Each provider is instantiated with its API key / base URL sourced
    from settings.  New providers can be added here without touching
    any route handler.
    """
    cfg = get_settings()

    router = ProviderRouter()

    router.register(
        OpenAIProvider(
            api_key=cfg.OPENAI_API_KEY,
            timeout=cfg.REQUEST_TIMEOUT_SECONDS,
        )
    )
    router.register(
        ClaudeProvider(
            api_key=cfg.CLAUDE_API_KEY,
            timeout=cfg.REQUEST_TIMEOUT_SECONDS,
        )
    )
    router.register(
        GeminiProvider(
            api_key=cfg.GEMINI_API_KEY,
            timeout=cfg.REQUEST_TIMEOUT_SECONDS,
        )
    )
    router.register(
        DeepSeekProvider(
            api_key=cfg.DEEPSEEK_API_KEY,
            base_url=cfg.DEEPSEEK_BASE_URL,
            timeout=cfg.REQUEST_TIMEOUT_SECONDS,
        )
    )
    router.register(
        GroqProvider(
            api_key=cfg.GROQ_API_KEY,
            base_url=cfg.GROQ_BASE_URL,
            timeout=cfg.REQUEST_TIMEOUT_SECONDS,
        )
    )
    router.register(
        OllamaProvider(
            base_url=cfg.OLLAMA_BASE_URL,
            timeout=cfg.REQUEST_TIMEOUT_SECONDS,
        )
    )

    return router


def get_provider_router() -> ProviderRouter:
    """FastAPI dependency — returns the ProviderRouter singleton."""
    return _build_provider_router()


def get_gateway_service(
    provider_router: Annotated[ProviderRouter, Depends(get_provider_router)],
) -> GatewayService:
    """
    FastAPI dependency — returns a GatewayService scoped to the request.

    GatewayService is stateless so constructing it per-request is safe
    and makes the dependency graph explicit.
    """
    return GatewayService(provider_router=provider_router)
