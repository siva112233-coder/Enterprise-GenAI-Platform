"""
DeepSeek provider implementation.

DeepSeek exposes an OpenAI-compatible API, so the integration
pattern mirrors OpenAI but targets a different base URL.

Placeholder: all I/O methods raise ``NotImplementedError``.
Replace method bodies with ``httpx`` or ``openai`` SDK calls
(pointed at ``DEEPSEEK_BASE_URL``) when ready.

Supported models:
    deepseek-chat, deepseek-reasoner
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
        id="deepseek-chat",
        name="DeepSeek Chat (V3)",
        context_window=64_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="deepseek-reasoner",
        name="DeepSeek Reasoner (R1)",
        context_window=64_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
]

# Cost per 1 000 tokens in USD (cache miss pricing, approximate)
_PRICING: Dict[str, Dict[str, float]] = {
    "deepseek-chat":     {"prompt": 0.00027, "completion": 0.00110},
    "deepseek-reasoner": {"prompt": 0.00055, "completion": 0.00219},
}


class DeepSeekProvider(LLMProvider):
    """
    Provider integration for DeepSeek AI (OpenAI-compatible API).

    Args:
        api_key:  DeepSeek API key.  If ``None``, health returns UNCONFIGURED.
        base_url: DeepSeek API base URL (default: https://api.deepseek.com/v1).
        timeout:  HTTP timeout in seconds.
    """

    def __init__(
        self,
        api_key: Optional[str],
        base_url: str = "https://api.deepseek.com/v1",
        timeout: float = 120.0,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout

    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return "deepseek"

    @property
    def display_name(self) -> str:
        return "DeepSeek AI"

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
        TODO: Implement using the OpenAI SDK pointing at DeepSeek's base URL.

        Example::

            import openai
            client = openai.AsyncOpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
            )
            resp = await client.chat.completions.create(
                model=model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=temperature,
                max_tokens=max_tokens,
            )
        """
        raise NotImplementedError(
            "DeepSeekProvider.chat() is not yet implemented. "
            "Use the OpenAI SDK with base_url=DeepSeek and replace this stub."
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
        TODO: Implement using OpenAI SDK with stream=True at DeepSeek base URL.
        """
        raise NotImplementedError("DeepSeekProvider.stream() is not yet implemented.")
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
        TODO: DeepSeek uses the same tokeniser family as OpenAI (tiktoken).

        Example::

            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        """
        raise NotImplementedError(
            "DeepSeekProvider.count_tokens() requires the 'tiktoken' package."
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
