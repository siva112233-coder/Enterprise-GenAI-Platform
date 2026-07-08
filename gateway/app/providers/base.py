"""
Abstract base class for all LLM providers.

Defines the contract that every concrete provider must fulfil.
New providers are added by:
  1. Inheriting from ``LLMProvider``
  2. Implementing all abstract methods
  3. Registering the instance in ``core/dependencies.py``

No other file needs to change — Open/Closed Principle in practice.
"""

from __future__ import annotations

import abc
from typing import Any, AsyncIterator, Dict, List, Optional

from app.schemas.chat import (
    ChatMessage,
    ChatResponse,
    ModelInfo,
    ProviderInfo,
    ProviderStatus,
    TokenUsage,
)


class LLMProvider(abc.ABC):
    """
    Abstract base class for LLM provider integrations.

    Implementors are responsible for translating the Gateway's
    canonical schema into provider-specific API calls and
    translating responses back.

    Thread/concurrency safety: all I/O methods are ``async``.
    """

    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Machine-readable provider slug (lowercase, no spaces).

        This value is used as the routing key — it must match
        what callers send in ``ChatRequest.provider``.

        Example: ``"openai"``, ``"claude"``, ``"gemini"``
        """

    @property
    @abc.abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name shown in API responses."""

    # ── Core LLM operations ──────────────────────────────────────────────────

    @abc.abstractmethod
    async def chat(
        self,
        *,
        model: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """
        Execute a single chat completion and return the full response.

        Args:
            model:       Provider-specific model identifier.
            messages:    Ordered list of conversation messages.
            temperature: Sampling temperature (0.0 – 2.0).
            max_tokens:  Cap on generated tokens.  ``None`` uses the
                         provider's default.
            **kwargs:    Provider-specific pass-through parameters.

        Returns:
            A populated ``ChatResponse`` instance.

        Raises:
            ProviderUnavailable: On network / API errors.
            InvalidModel:        If ``model`` is not supported.
        """

    @abc.abstractmethod
    async def stream(
        self,
        *,
        model: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion as an async iterator of text chunks.

        Each yielded value is a raw text delta from the provider.
        The caller is responsible for accumulating deltas.

        Yields:
            str — incremental response text.

        Raises:
            ProviderUnavailable: On network / API errors.
            InvalidModel:        If ``model`` is not supported.
        """

    # ── Introspection ─────────────────────────────────────────────────────────

    @abc.abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """
        Return the list of models supported by this provider.

        Implementations may return a static list or query the
        provider's API dynamically.
        """

    @abc.abstractmethod
    async def health(self) -> ProviderStatus:
        """
        Perform a lightweight health / connectivity check.

        Returns:
            ``ProviderStatus.HEALTHY``      — reachable and configured.
            ``ProviderStatus.DEGRADED``     — reachable but slow / partial.
            ``ProviderStatus.UNAVAILABLE``  — unreachable or API error.
            ``ProviderStatus.UNCONFIGURED`` — API key / URL not set.
        """

    # ── Token accounting ──────────────────────────────────────────────────────

    @abc.abstractmethod
    def count_tokens(self, text: str, model: str) -> int:
        """
        Estimate the token count for ``text`` using ``model``'s tokeniser.

        This is a *synchronous* method because tokenisation is CPU-bound
        and should not require network I/O.

        Args:
            text:  The string to tokenise.
            model: Model identifier (tokeniser may vary per model family).

        Returns:
            Estimated token count as an integer.
        """

    @abc.abstractmethod
    def estimate_cost(
        self,
        usage: TokenUsage,
        model: str,
    ) -> Dict[str, float]:
        """
        Calculate the estimated cost for a given ``TokenUsage`` object.

        Args:
            usage: Token counts from a completed request.
            model: Model identifier (pricing varies per model).

        Returns:
            A dict with at minimum ``{"total_usd": float}``.
            Providers may include ``"prompt_usd"`` and
            ``"completion_usd"`` breakdowns.

        Note:
            This is an *estimate* — actual billing may differ.
            The Gateway does NOT store or act on cost data.
        """

    # ── Utility ───────────────────────────────────────────────────────────────

    async def get_provider_info(self) -> ProviderInfo:
        """
        Return a ``ProviderInfo`` summary including live health status.

        This convenience method composes ``health()`` and ``list_models()``
        and is used by the ``GET /api/v1/providers`` endpoint.
        """
        status = await self.health()
        try:
            models = await self.list_models()
            model_ids = [m.id for m in models]
        except Exception:
            model_ids = []

        return ProviderInfo(
            name=self.name,
            display_name=self.display_name,
            status=status,
            models=model_ids,
            configured=status != ProviderStatus.UNCONFIGURED,
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
