"""
Ollama provider implementation.

Ollama runs models locally and exposes an OpenAI-compatible HTTP API.
Because the model catalogue is dynamic (depends on what the user has
pulled), ``list_models()`` queries the Ollama REST API at runtime.

Placeholder: chat/stream I/O methods raise ``NotImplementedError``.
Replace with ``httpx`` calls against ``OLLAMA_BASE_URL`` when ready.

Default base URL: http://localhost:11434
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

# Static fallback model list — shown when Ollama is reachable but
# the dynamic query has not been made yet.
_FALLBACK_MODELS: List[ModelInfo] = [
    ModelInfo(
        id="llama3.2",
        name="Llama 3.2 (3B)",
        context_window=128_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="llama3.1",
        name="Llama 3.1 (8B)",
        context_window=128_000,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="mistral",
        name="Mistral 7B",
        context_window=32_768,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="gemma3",
        name="Gemma 3 (4B)",
        context_window=8_192,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="phi4",
        name="Phi-4 (14B)",
        context_window=16_384,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
    ModelInfo(
        id="qwen2.5-coder",
        name="Qwen 2.5 Coder (7B)",
        context_window=32_768,
        supports_streaming=True,
        supports_system_prompt=True,
    ),
]


class OllamaProvider(LLMProvider):
    """
    Provider integration for Ollama (local LLM server).

    Ollama has no API key — authentication is implicit (local network).
    Health check is a lightweight ``GET /api/tags`` ping.

    Args:
        base_url: Ollama server URL (default: http://localhost:11434).
        timeout:  HTTP timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def display_name(self) -> str:
        return "Ollama (Local)"

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
        TODO: Implement using ``httpx.AsyncClient`` against Ollama's API.

        Example::

            async with httpx.AsyncClient(base_url=self._base_url) as client:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": m.role, "content": m.content} for m in messages
                    ],
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        **({"num_predict": max_tokens} if max_tokens else {}),
                    },
                }
                resp = await client.post(
                    "/api/chat", json=payload, timeout=self._timeout
                )
                resp.raise_for_status()
        """
        raise NotImplementedError(
            "OllamaProvider.chat() is not yet implemented. "
            "Use httpx to call the Ollama /api/chat endpoint."
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
        TODO: Implement using ``httpx.AsyncClient`` with ``stream=True``.
        Ollama returns newline-delimited JSON for streaming responses.
        """
        raise NotImplementedError("OllamaProvider.stream() is not yet implemented.")
        yield  # type: ignore[misc]

    # ── Introspection ─────────────────────────────────────────────────────────

    async def list_models(self) -> List[ModelInfo]:
        """
        TODO: Query ``GET /api/tags`` to get dynamically installed models.

        Example::

            async with httpx.AsyncClient(base_url=self._base_url) as client:
                resp = await client.get("/api/tags", timeout=5.0)
                resp.raise_for_status()
                data = resp.json()
                return [
                    ModelInfo(id=m["name"], name=m["name"])
                    for m in data.get("models", [])
                ]

        Falls back to static list on error.
        """
        return _FALLBACK_MODELS

    async def health(self) -> ProviderStatus:
        """
        TODO: Ping ``GET /`` (Ollama returns 200 "Ollama is running").

        Example::

            async with httpx.AsyncClient(base_url=self._base_url) as client:
                try:
                    resp = await client.get("/", timeout=3.0)
                    return ProviderStatus.HEALTHY if resp.status_code == 200
                           else ProviderStatus.DEGRADED
                except Exception:
                    return ProviderStatus.UNAVAILABLE
        """
        # No API key required — report HEALTHY by default.
        # Real health check should ping the Ollama server.
        return ProviderStatus.HEALTHY

    # ── Token accounting ──────────────────────────────────────────────────────

    def count_tokens(self, text: str, model: str) -> int:
        """
        TODO: Ollama does not expose a direct token-count endpoint.

        Rough approximation: 1 token ≈ 4 characters.
        Replace with a model-specific tokeniser for accuracy.
        """
        # Rough approximation until a proper tokeniser is wired in
        return max(1, len(text) // 4)

    def estimate_cost(self, usage: TokenUsage, model: str) -> Dict[str, float]:
        """Ollama runs locally — no API cost."""
        return {
            "prompt_usd": 0.0,
            "completion_usd": 0.0,
            "total_usd": 0.0,
        }
