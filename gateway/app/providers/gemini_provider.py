"""
Google Gemini provider implementation.

Placeholder: all I/O methods raise ``NotImplementedError``.
Replace method bodies with actual ``google-generativeai`` SDK calls when ready.

Supported models:
    gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash, gemini-1.0-pro
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
        id="gemini-2.0-flash",
        name="Gemini 2.0 Flash",
        context_window=1_048_576,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="gemini-1.5-pro",
        name="Gemini 1.5 Pro",
        context_window=2_097_152,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="gemini-1.5-flash",
        name="Gemini 1.5 Flash",
        context_window=1_048_576,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="gemini-1.0-pro",
        name="Gemini 1.0 Pro",
        context_window=32_760,
        supports_streaming=True,
        supports_system_prompt=False,
    ),
]

# Cost per 1 000 tokens in USD (approximate, varies by prompt length tier)
_PRICING: Dict[str, Dict[str, float]] = {
    "gemini-2.0-flash": {"prompt": 0.00010, "completion": 0.00040},
    "gemini-1.5-pro":   {"prompt": 0.00125, "completion": 0.00500},
    "gemini-1.5-flash": {"prompt": 0.000075,"completion": 0.00030},
    "gemini-1.0-pro":   {"prompt": 0.000500,"completion": 0.00150},
}


class GeminiProvider(LLMProvider):
    """
    Provider integration for Google Gemini Generative AI API.

    Args:
        api_key:  Google AI API key (from ``aistudio.google.com``).
                  If ``None``, health returns UNCONFIGURED.
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
        return "gemini"

    @property
    def display_name(self) -> str:
        return "Google Gemini"

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
        TODO: Implement using ``google.generativeai``.

        Example::

            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            gemini_model = genai.GenerativeModel(model)
            chat = gemini_model.start_chat(history=[...])
            response = await chat.send_message_async(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )
        """
        raise NotImplementedError(
            "GeminiProvider.chat() is not yet implemented. "
            "Install 'google-generativeai' and replace this stub."
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
        TODO: Implement using ``GenerativeModel.generate_content_async`` with ``stream=True``.
        """
        raise NotImplementedError("GeminiProvider.stream() is not yet implemented.")
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
        TODO: Implement using ``genai.GenerativeModel(model).count_tokens(text)``.
        Google provides a synchronous token counter via the SDK.
        """
        raise NotImplementedError(
            "GeminiProvider.count_tokens() requires the 'google-generativeai' package."
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
