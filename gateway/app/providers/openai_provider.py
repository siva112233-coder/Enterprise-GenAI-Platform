"""
OpenAI provider implementation.

Placeholder: all I/O methods raise ``NotImplementedError``.
Replace the method bodies with actual ``openai`` SDK calls when ready.

Supported models (static list — update as OpenAI releases new versions):
    gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo
"""

from __future__ import annotations

from typing import Any, AsyncIterator, Dict, List, Optional

from app.providers.base import LLMProvider
from app.schemas.chat import (
    ChatMessage,
    ChatResponse,
    ModelInfo,
    ProviderStatus,
    TokenUsage,
)


_SUPPORTED_MODELS: List[ModelInfo] = [
    ModelInfo(
        id="gpt-4o",
        name="GPT-4o",
        context_window=128_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="gpt-4o-mini",
        name="GPT-4o Mini",
        context_window=128_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="gpt-4-turbo",
        name="GPT-4 Turbo",
        context_window=128_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="gpt-4",
        name="GPT-4",
        context_window=8_192,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="gpt-3.5-turbo",
        name="GPT-3.5 Turbo",
        context_window=16_385,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
]

# Cost per 1 000 tokens in USD (approximate, as of 2025-Q1)
_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o":        {"prompt": 0.005,    "completion": 0.015},
    "gpt-4o-mini":   {"prompt": 0.00015,  "completion": 0.0006},
    "gpt-4-turbo":   {"prompt": 0.01,     "completion": 0.03},
    "gpt-4":         {"prompt": 0.03,     "completion": 0.06},
    "gpt-3.5-turbo": {"prompt": 0.0005,   "completion": 0.0015},
}


class OpenAIProvider(LLMProvider):
    """
    Provider integration for OpenAI Chat Completions API.

    Args:
        api_key:  OpenAI API key.  If ``None``, ``health()`` returns
                  ``UNCONFIGURED`` and all I/O raises ``NotImplementedError``.
        timeout:  HTTP timeout in seconds for provider requests.
    """

    def __init__(
        self,
        api_key: Optional[str],
        timeout: float = 120.0,
    ) -> None:
        self._api_key = api_key
        self._timeout = timeout

    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return "openai"

    @property
    def display_name(self) -> str:
        return "OpenAI"

    # ── Core LLM operations ──────────────────────────────────────────────────

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
        TODO: Implement using ``openai.AsyncOpenAI``.

        Example::

            client = openai.AsyncOpenAI(api_key=self._api_key)
            resp = await client.chat.completions.create(
                model=model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=temperature,
                max_tokens=max_tokens,
            )
        """
        raise NotImplementedError(
            "OpenAIProvider.chat() is not yet implemented. "
            "Install 'openai' and replace this stub."
        )

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
        TODO: Implement using ``openai.AsyncOpenAI`` with ``stream=True``.
        """
        raise NotImplementedError("OpenAIProvider.stream() is not yet implemented.")
        # Make the generator valid Python by including a yield
        # (unreachable but satisfies type checkers)
        yield  # type: ignore[misc]

    # ── Introspection ─────────────────────────────────────────────────────────

    async def list_models(self) -> List[ModelInfo]:
        """Return static model catalogue for OpenAI."""
        return _SUPPORTED_MODELS

    async def health(self) -> ProviderStatus:
        """
        Return UNCONFIGURED if no API key is set, otherwise HEALTHY.

        TODO: Replace with a live ``GET /models`` ping when integrating
        the actual OpenAI SDK.
        """
        if not self._api_key:
            return ProviderStatus.UNCONFIGURED
        return ProviderStatus.HEALTHY

    # ── Token accounting ──────────────────────────────────────────────────────

    def count_tokens(self, text: str, model: str) -> int:
        """
        TODO: Implement using ``tiktoken``.

        Example::

            import tiktoken
            enc = tiktoken.encoding_for_model(model)
            return len(enc.encode(text))
        """
        raise NotImplementedError(
            "OpenAIProvider.count_tokens() requires the 'tiktoken' package."
        )

    def estimate_cost(self, usage: TokenUsage, model: str) -> Dict[str, float]:
        """Calculate estimated USD cost from token counts."""
        pricing = _PRICING.get(model, {"prompt": 0.0, "completion": 0.0})
        prompt_cost = ((usage.prompt_tokens or 0) / 1_000) * pricing["prompt"]
        completion_cost = ((usage.completion_tokens or 0) / 1_000) * pricing["completion"]
        return {
            "prompt_usd": round(prompt_cost, 6),
            "completion_usd": round(completion_cost, 6),
            "total_usd": round(prompt_cost + completion_cost, 6),
        }
