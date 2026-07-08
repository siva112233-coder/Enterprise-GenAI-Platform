"""
Groq provider implementation.

Groq exposes an OpenAI-compatible API served on their LPU inference
hardware.  The integration pattern mirrors OpenAI but targets a
different base URL.

Placeholder: all I/O methods raise ``NotImplementedError``.

Supported models:
    llama-3.3-70b-versatile, llama-3.1-8b-instant,
    mixtral-8x7b-32768, gemma2-9b-it
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
        id="llama-3.3-70b-versatile",
        name="Llama 3.3 70B Versatile",
        context_window=128_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="llama-3.1-8b-instant",
        name="Llama 3.1 8B Instant",
        context_window=128_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="mixtral-8x7b-32768",
        name="Mixtral 8x7B",
        context_window=32_768,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="gemma2-9b-it",
        name="Gemma 2 9B IT",
        context_window=8_192,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
]

# Groq pricing (approximate, per 1 000 tokens in USD)
_PRICING: Dict[str, Dict[str, float]] = {
    "llama-3.3-70b-versatile": {"prompt": 0.00059, "completion": 0.00079},
    "llama-3.1-8b-instant":    {"prompt": 0.00005, "completion": 0.00008},
    "mixtral-8x7b-32768":      {"prompt": 0.00024, "completion": 0.00024},
    "gemma2-9b-it":            {"prompt": 0.00020, "completion": 0.00020},
}


class GroqProvider(LLMProvider):
    """
    Provider integration for Groq LPU Inference (OpenAI-compatible API).

    Args:
        api_key:  Groq API key.  If ``None``, health returns UNCONFIGURED.
        base_url: Groq API base URL (default: https://api.groq.com/openai/v1).
        timeout:  HTTP timeout in seconds.
    """

    def __init__(
        self,
        api_key: Optional[str],
        base_url: str = "https://api.groq.com/openai/v1",
        timeout: float = 120.0,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout

    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return "groq"

    @property
    def display_name(self) -> str:
        return "Groq"

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
        TODO: Implement using the OpenAI SDK pointing at Groq's base URL.

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
            "GroqProvider.chat() is not yet implemented. "
            "Use the OpenAI SDK with base_url=Groq and replace this stub."
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
        TODO: Implement using OpenAI SDK with stream=True at Groq base URL.
        """
        raise NotImplementedError("GroqProvider.stream() is not yet implemented.")
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
        TODO: Groq serves Llama / Mixtral models — use their respective tokenisers.

        Example for Llama::

            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
            return len(tokenizer.encode(text))
        """
        raise NotImplementedError(
            "GroqProvider.count_tokens() requires model-specific tokeniser packages."
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
