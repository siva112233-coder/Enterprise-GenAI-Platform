"""
Anthropic Claude provider implementation.

Placeholder: all I/O methods raise ``NotImplementedError``.
Replace method bodies with actual ``anthropic`` SDK calls when ready.

Supported models:
    claude-opus-4-5, claude-sonnet-4-5, claude-haiku-3-5, claude-3-opus,
    claude-3-sonnet, claude-3-haiku
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
        id="claude-opus-4-5",
        name="Claude Opus 4.5",
        context_window=200_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="claude-sonnet-4-5",
        name="Claude Sonnet 4.5",
        context_window=200_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="claude-haiku-3-5",
        name="Claude Haiku 3.5",
        context_window=200_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="claude-3-opus-20240229",
        name="Claude 3 Opus",
        context_window=200_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="claude-3-sonnet-20240229",
        name="Claude 3 Sonnet",
        context_window=200_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="claude-3-haiku-20240307",
        name="Claude 3 Haiku",
        context_window=200_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
]

# Cost per 1 000 tokens in USD (approximate)
_PRICING: Dict[str, Dict[str, float]] = {
    "claude-opus-4-5":          {"prompt": 0.015,  "completion": 0.075},
    "claude-sonnet-4-5":        {"prompt": 0.003,  "completion": 0.015},
    "claude-haiku-3-5":         {"prompt": 0.0008, "completion": 0.004},
    "claude-3-opus-20240229":   {"prompt": 0.015,  "completion": 0.075},
    "claude-3-sonnet-20240229": {"prompt": 0.003,  "completion": 0.015},
    "claude-3-haiku-20240307":  {"prompt": 0.00025,"completion": 0.00125},
}


class ClaudeProvider(LLMProvider):
    """
    Provider integration for Anthropic Claude Messages API.

    Args:
        api_key:  Anthropic API key.  If ``None``, health returns UNCONFIGURED.
        timeout:  HTTP timeout in seconds.
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
        return "claude"

    @property
    def display_name(self) -> str:
        return "Anthropic Claude"

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
        TODO: Implement using ``anthropic.AsyncAnthropic``.

        Example::

            client = anthropic.AsyncAnthropic(api_key=self._api_key)
            # Extract system message if present
            system = next((m.content for m in messages if m.role == "system"), "")
            human_messages = [
                {"role": m.role, "content": m.content}
                for m in messages if m.role != "system"
            ]
            resp = await client.messages.create(
                model=model,
                system=system,
                messages=human_messages,
                temperature=temperature,
                max_tokens=max_tokens or 4096,
            )
        """
        raise NotImplementedError(
            "ClaudeProvider.chat() is not yet implemented. "
            "Install 'anthropic' and replace this stub."
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
        TODO: Implement using ``anthropic.AsyncAnthropic`` with streaming.
        """
        raise NotImplementedError("ClaudeProvider.stream() is not yet implemented.")
        yield  # type: ignore[misc]

    # ── Introspection ─────────────────────────────────────────────────────────

    async def list_models(self) -> List[ModelInfo]:
        return _SUPPORTED_MODELS

    async def health(self) -> ProviderStatus:
        if not self._api_key:
            return ProviderStatus.UNCONFIGURED
        return ProviderStatus.HEALTHY

    # ── Token accounting ──────────────────────────────────────────────────────

    def count_tokens(self, text: str, model: str) -> int:
        """
        TODO: Implement using ``anthropic.Anthropic().count_tokens()``.
        Anthropic provides a synchronous token counter via the SDK.
        """
        raise NotImplementedError(
            "ClaudeProvider.count_tokens() requires the 'anthropic' package."
        )

    def estimate_cost(self, usage: TokenUsage, model: str) -> Dict[str, float]:
        pricing = _PRICING.get(model, {"prompt": 0.0, "completion": 0.0})
        prompt_cost = ((usage.prompt_tokens or 0) / 1_000) * pricing["prompt"]
        completion_cost = ((usage.completion_tokens or 0) / 1_000) * pricing["completion"]
        return {
            "prompt_usd": round(prompt_cost, 6),
            "completion_usd": round(completion_cost, 6),
            "total_usd": round(prompt_cost + completion_cost, 6),
        }
