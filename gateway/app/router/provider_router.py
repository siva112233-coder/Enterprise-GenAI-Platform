"""
ProviderRouter — registry and selector for LLM provider instances.

Responsibilities:
  - Accept provider registrations at startup
  - Select a provider by name (routing key)
  - Enumerate registered providers and their models
  - Raise typed exceptions when providers are missing or unavailable

Design principles:
  - Open/Closed: new providers are added via ``register()``,
    no existing code needs to change
  - Single Responsibility: routing only — no business logic
  - Dependency Injection: the router itself is injected into services
"""

from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

from app.exceptions.gateway import ProviderNotFound, ProviderUnavailable
from app.providers.base import LLMProvider
from app.schemas.chat import ModelInfo, ProviderInfo, ProviderStatus


class ProviderRouter:
    """
    Registry for LLM provider instances.

    Thread-safety: registrations happen once at startup (inside
    ``_build_provider_router``), which is protected by ``lru_cache``.
    Concurrent reads during request handling are safe.
    """

    def __init__(self) -> None:
        # Mapping of provider slug → provider instance
        self._providers: Dict[str, LLMProvider] = {}

    # ── Registration ──────────────────────────────────────────────────────────

    def register(self, provider: LLMProvider) -> None:
        """
        Register a provider instance.

        The routing key is ``provider.name`` (lowercase slug).
        Re-registering the same name overwrites the previous instance —
        this allows hot-swapping in tests.

        Args:
            provider: A concrete ``LLMProvider`` instance.
        """
        self._providers[provider.name] = provider

    def unregister(self, name: str) -> None:
        """
        Remove a provider from the registry.

        Useful in test fixtures.  Silently ignores unknown names.
        """
        self._providers.pop(name, None)

    # ── Selection ─────────────────────────────────────────────────────────────

    def get(self, name: str) -> LLMProvider:
        """
        Return the provider registered under ``name``.

        Args:
            name: Provider slug (case-insensitive).

        Returns:
            The ``LLMProvider`` instance.

        Raises:
            ProviderNotFound: If no provider is registered under ``name``.
        """
        key = name.strip().lower()
        provider = self._providers.get(key)
        if provider is None:
            available = ", ".join(sorted(self._providers.keys())) or "none"
            raise ProviderNotFound(
                f"Provider '{name}' is not registered. "
                f"Available providers: [{available}]"
            )
        return provider

    def get_or_none(self, name: str) -> Optional[LLMProvider]:
        """Return the provider or ``None`` without raising."""
        return self._providers.get(name.strip().lower())

    # ── Enumeration ───────────────────────────────────────────────────────────

    def list_provider_names(self) -> List[str]:
        """Return sorted list of registered provider slugs."""
        return sorted(self._providers.keys())

    async def list_providers(self) -> List[ProviderInfo]:
        """
        Return ``ProviderInfo`` for all registered providers.

        Runs health checks concurrently via ``asyncio.gather`` to avoid
        sequential latency when many providers are registered.
        """
        tasks = [p.get_provider_info() for p in self._providers.values()]
        results: List[ProviderInfo] = await asyncio.gather(*tasks, return_exceptions=False)
        return sorted(results, key=lambda p: p.name)

    async def list_all_models(self) -> List[ModelInfo]:
        """
        Return the combined model catalogue across all registered providers.

        Models from unavailable / unconfigured providers are included —
        they will simply fail at request time with a ``ProviderUnavailable``
        error.
        """
        all_models: List[ModelInfo] = []
        for provider in self._providers.values():
            try:
                models = await provider.list_models()
                all_models.extend(models)
            except Exception:
                # If a provider fails to enumerate its models, skip it
                pass
        return all_models

    # ── Validation helpers ────────────────────────────────────────────────────

    async def assert_provider_healthy(self, name: str) -> LLMProvider:
        """
        Retrieve a provider and assert it is not ``UNAVAILABLE``.

        Args:
            name: Provider slug.

        Returns:
            The healthy ``LLMProvider`` instance.

        Raises:
            ProviderNotFound:    If provider does not exist.
            ProviderUnavailable: If provider health check returns UNAVAILABLE.
        """
        provider = self.get(name)
        status = await provider.health()
        if status == ProviderStatus.UNAVAILABLE:
            raise ProviderUnavailable(
                name,
                reason="Provider health check returned UNAVAILABLE.",
            )
        return provider

    # ── Dunder ────────────────────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self._providers)

    def __contains__(self, name: str) -> bool:
        return name.strip().lower() in self._providers

    def __repr__(self) -> str:
        names = ", ".join(sorted(self._providers.keys()))
        return f"<ProviderRouter providers=[{names}]>"
