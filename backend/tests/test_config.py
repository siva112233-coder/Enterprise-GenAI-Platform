"""
Tests for application configuration.

Verifies:
- Settings loads correctly with defaults
- Computed DATABASE_URL and SYNC_DATABASE_URL are well-formed
- Production safety validator correctly rejects insecure config
- Settings singleton is cached (same object returned on repeated calls)
"""

import pytest

from app.core.config import Settings, get_settings


class TestSettings:
    """Test suite for application configuration loading."""

    def test_settings_load_with_defaults(self) -> None:
        """Settings must load successfully with default values."""
        settings = Settings(
            ENVIRONMENT="development",
            POSTGRES_HOST="localhost",
            POSTGRES_USER="user",
            POSTGRES_PASSWORD="pass",
            POSTGRES_DB="db",
        )
        assert settings.APP_NAME == "Enterprise GenAI Platform"
        assert settings.ENVIRONMENT == "development"

    def test_database_url_scheme_is_asyncpg(self) -> None:
        """Async DATABASE_URL must use the asyncpg driver scheme."""
        settings = Settings(
            POSTGRES_HOST="db",
            POSTGRES_USER="user",
            POSTGRES_PASSWORD="pass",
            POSTGRES_DB="mydb",
        )
        db_url = str(settings.DATABASE_URL)
        assert db_url.startswith("postgresql+asyncpg://")
        assert "mydb" in db_url

    def test_sync_database_url_scheme_is_psycopg2(self) -> None:
        """Sync SYNC_DATABASE_URL must use the psycopg2 driver scheme (for Alembic)."""
        settings = Settings(
            POSTGRES_HOST="db",
            POSTGRES_USER="user",
            POSTGRES_PASSWORD="pass",
            POSTGRES_DB="mydb",
        )
        sync_url = str(settings.SYNC_DATABASE_URL)
        assert sync_url.startswith("postgresql+psycopg2://")

    def test_production_rejects_default_secret_key(self) -> None:
        """Production environment must not allow the default SECRET_KEY."""
        with pytest.raises(ValueError, match="SECRET_KEY"):
            Settings(
                ENVIRONMENT="production",
                DEBUG=False,
                DB_ECHO=False,
                SECRET_KEY="CHANGE_ME_IN_PRODUCTION_USE_SECRETS_MANAGER",
                POSTGRES_HOST="db",
                POSTGRES_USER="user",
                POSTGRES_PASSWORD="pass",
                POSTGRES_DB="db",
            )

    def test_production_rejects_debug_true(self) -> None:
        """Production environment must not allow DEBUG=True."""
        with pytest.raises(ValueError, match="DEBUG"):
            Settings(
                ENVIRONMENT="production",
                DEBUG=True,
                DB_ECHO=False,
                SECRET_KEY="a-valid-production-secret-key-thats-long-enough",
                POSTGRES_HOST="db",
                POSTGRES_USER="user",
                POSTGRES_PASSWORD="pass",
                POSTGRES_DB="db",
            )

    def test_is_development_flag(self) -> None:
        """is_development property returns True only in development."""
        dev_settings = Settings(ENVIRONMENT="development")
        prod_settings = Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            DB_ECHO=False,
            SECRET_KEY="a-valid-production-secret-key-thats-long-enough",
        )
        assert dev_settings.is_development is True
        assert prod_settings.is_development is False

    def test_get_settings_returns_singleton(self) -> None:
        """get_settings() must return the same cached object on every call."""
        settings_a = get_settings()
        settings_b = get_settings()
        assert settings_a is settings_b
