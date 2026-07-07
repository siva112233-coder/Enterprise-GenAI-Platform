"""
Core configuration module for the Enterprise GenAI Platform.

Loads and validates all environment variables using Pydantic Settings.
Follows the 12-Factor App methodology for configuration management.
"""

from functools import lru_cache
from typing import Annotated, Any

from pydantic import AnyUrl, BeforeValidator, PostgresDsn, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_cors_origins(v: Any) -> list[str] | str:
    """Parse CORS origins from a comma-separated string or list."""
    if isinstance(v, str) and not v.startswith("["):
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    elif isinstance(v, list):
        return v
    return v


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All fields can be overridden via environment variables (case-insensitive).
    Sensitive values should be provided via .env file or secrets management.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars not defined here
    )

    # ---------------------------------------------------------------------------
    # Application
    # ---------------------------------------------------------------------------
    APP_NAME: str = "Enterprise GenAI Platform"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "Enterprise-grade AI Gateway with multi-provider LLM support, "
        "observability, cost monitoring, and agentic workflow orchestration."
    )
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ---------------------------------------------------------------------------
    # Server
    # ---------------------------------------------------------------------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # ---------------------------------------------------------------------------
    # Database (PostgreSQL)
    # ---------------------------------------------------------------------------
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "genai_user"
    POSTGRES_PASSWORD: str = "changeme"
    POSTGRES_DB: str = "genai_platform"

    # SQLAlchemy connection pool settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800  # 30 minutes
    DB_ECHO: bool = False  # Set True to log all SQL statements

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        """Construct the async PostgreSQL DSN from individual components."""
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SYNC_DATABASE_URL(self) -> PostgresDsn:
        """
        Construct the synchronous PostgreSQL DSN.
        Used exclusively by Alembic for migration management.
        """
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # ---------------------------------------------------------------------------
    # Logging
    # ---------------------------------------------------------------------------
    LOG_LEVEL: str = "INFO"  # DEBUG | INFO | WARNING | ERROR | CRITICAL
    LOG_FORMAT: str = "json"  # json | text
    LOG_FILE_PATH: str | None = None  # Optional file-based logging

    # ---------------------------------------------------------------------------
    # CORS
    # ---------------------------------------------------------------------------
    CORS_ORIGINS: Annotated[list[str] | str, BeforeValidator(_parse_cors_origins)] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # ---------------------------------------------------------------------------
    # Security (Placeholders — implemented in a future module)
    # ---------------------------------------------------------------------------
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_SECRETS_MANAGER"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # ---------------------------------------------------------------------------
    # Validators
    # ---------------------------------------------------------------------------
    @model_validator(mode="after")
    def _validate_production_settings(self) -> "Settings":
        """
        Enforce stricter security constraints in production environments.
        Raises ValueError early at startup rather than failing silently.
        """
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "CHANGE_ME_IN_PRODUCTION_USE_SECRETS_MANAGER":
                raise ValueError(
                    "SECRET_KEY must be changed from the default value in production."
                )
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production.")
            if self.DB_ECHO:
                raise ValueError(
                    "DB_ECHO must be False in production to prevent SQL leakage."
                )
        return self

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    @property
    def is_development(self) -> bool:
        """Returns True when running in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Returns True when running in production mode."""
        return self.ENVIRONMENT == "production"

    @property
    def is_testing(self) -> bool:
        """Returns True when running in test mode."""
        return self.ENVIRONMENT == "testing"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached singleton instance of Settings.

    Using lru_cache ensures environment variables are read exactly once,
    making the application startup deterministic and efficient.

    Returns:
        Settings: The validated, cached application settings instance.
    """
    return Settings()
