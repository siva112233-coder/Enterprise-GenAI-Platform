# Alembic migration environment configuration.
# This file is executed by Alembic's CLI (`alembic upgrade head`, etc.)
# and controls how migrations are discovered, generated, and applied.

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Import Base metadata so Alembic autogenerate can detect model changes
# ---------------------------------------------------------------------------
# IMPORTANT: Import ALL model modules here so their classes are registered
# on Base.metadata before autogenerate inspects it.
# As new models are added to app/models/, import them below, e.g.:
#
#   from app.models.user import User      # noqa: F401
#   from app.models.provider import LLMProvider  # noqa: F401
#
from app.db.base import Base  # noqa: F401
import app.models  # noqa: F401

# ---------------------------------------------------------------------------
# Application settings (provides the synchronous DATABASE_URL for Alembic)
# ---------------------------------------------------------------------------
from app.core.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Alembic Config object (provides access to alembic.ini values)
# ---------------------------------------------------------------------------
config = context.config

# Configure Python stdlib logging from the alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject the database URL from application settings.
# This overrides the sqlalchemy.url value in alembic.ini so we have a single
# source of truth for database connection strings.
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))

# Provide Base.metadata so autogenerate can diff against the live schema
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline migration (generates SQL scripts without a live DB connection)
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.

    Useful for generating SQL migration scripts to be reviewed and applied
    by a DBA, or in environments where a direct DB connection is unavailable.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Include naming conventions in comparison to detect constraint renames
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migration (applies migrations against a live DB connection)
# ---------------------------------------------------------------------------
def do_run_migrations(connection: Connection) -> None:
    """Execute migrations within an active database connection context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations asynchronously using asyncpg.

    Note: Alembic's CLI is synchronous, but we bridge to async here using
    asyncio.run() so we can use the same async engine configuration as the
    application. The sync psycopg2 URL is used for the actual migration runner
    via the ``run_sync`` bridge.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in online mode with a live database connection."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
