"""
Global Constants for the Enterprise GenAI Platform.
"""

from typing import Final

# LLM Providers
PROVIDER_OPENAI: Final[str] = "openai"
PROVIDER_ANTHROPIC: Final[str] = "anthropic"
PROVIDER_GEMINI: Final[str] = "gemini"
PROVIDER_DEEPSEEK: Final[str] = "deepseek"
PROVIDER_GROQ: Final[str] = "groq"
PROVIDER_OLLAMA: Final[str] = "ollama"

# Service names
SERVICE_BACKEND: Final[str] = "backend"
SERVICE_GATEWAY: Final[str] = "gateway"
SERVICE_LANGGRAPH: Final[str] = "langgraph-service"

# Environments
ENV_DEVELOPMENT: Final[str] = "development"
ENV_STAGING: Final[str] = "staging"
ENV_PRODUCTION: Final[str] = "production"
