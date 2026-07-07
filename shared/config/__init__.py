"""
Shared configuration loaders and validation logic using Pydantic Settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    """
    Base configuration for all services in the Enterprise GenAI Platform.
    Loads values from environment variables or a local .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Core configs
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    JWT_SECRET: Optional[str] = None

    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OLLAMA_URL: Optional[str] = None
