"""
Gateway-specific settings.

Extends BaseServiceSettings from shared/ with gateway-only configuration.
All values are sourced from environment variables or .env file.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import SettingsConfigDict
from shared.config import BaseServiceSettings


class GatewaySettings(BaseServiceSettings):
    """
    Configuration for the AI Gateway microservice.

    Inherits all shared settings (API keys, environment, etc.)
    and adds gateway-specific tunables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Service identity ──────────────────────────────────────────────────────
    SERVICE_NAME: str = "ai-gateway"
    SERVICE_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    # ── Server ────────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # ── Request limits ────────────────────────────────────────────────────────
    REQUEST_TIMEOUT_SECONDS: float = Field(
        default=120.0,
        description="Max seconds to wait for a provider response.",
    )
    MAX_TOKENS_CEILING: int = Field(
        default=16_384,
        description="Hard ceiling on max_tokens accepted in a ChatRequest.",
    )
    DEFAULT_TEMPERATURE: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Default sampling temperature when not specified by caller.",
    )

    # ── Provider defaults ─────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Base URL for the local Ollama server.",
    )
    DEEPSEEK_BASE_URL: str = Field(
        default="https://api.deepseek.com/v1",
        description="DeepSeek API base URL.",
    )
    GROQ_BASE_URL: str = Field(
        default="https://api.groq.com/openai/v1",
        description="Groq API base URL (OpenAI-compatible).",
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins.",
    )

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG | INFO | WARNING | ERROR).",
    )
    LOG_FORMAT: str = Field(
        default="json",
        description="Log format: 'json' for structured output, 'console' for dev.",
    )


# Module-level singleton — imported by other modules via DI or directly.
settings = GatewaySettings()
