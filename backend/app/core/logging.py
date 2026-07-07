"""
Structured logging configuration for the Enterprise GenAI Platform.

Provides JSON-structured logging via structlog for machine-readable output
in production, and human-friendly console output in development.

Key features:
- JSON log format for log aggregators (Datadog, ELK, Cloud Logging)
- Human-readable colored output for local development
- Request-scoped context binding (trace_id, request_id, user_id)
- Automatic stdlib logging integration (uvicorn, sqlalchemy, etc.)
- ISO 8601 timestamps
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, WrappedLogger

from app.core.config import get_settings

# ---------------------------------------------------------------------------
# Custom processors
# ---------------------------------------------------------------------------


def _add_app_context(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """
    Inject static application metadata into every log record.

    This allows log aggregators to filter, group, and alert on logs
    by application name and version without additional configuration.
    """
    settings = get_settings()
    event_dict["app"] = settings.APP_NAME
    event_dict["version"] = settings.APP_VERSION
    event_dict["environment"] = settings.ENVIRONMENT
    return event_dict


def _drop_color_message_key(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """
    Remove uvicorn's 'color_message' key from log records.

    Uvicorn adds this key with ANSI escape codes for terminal coloring.
    It is redundant in structured/JSON logs and pollutes the output.
    """
    event_dict.pop("color_message", None)
    return event_dict


# ---------------------------------------------------------------------------
# Setup function
# ---------------------------------------------------------------------------


def setup_logging() -> None:
    """
    Configure structlog and the standard library logging integration.

    Must be called once at application startup (in main.py lifespan).
    Subsequent calls are idempotent due to structlog's internal state.

    The pipeline is:
        stdlib logging events
            → structlog bridge
            → shared processor chain
            → renderer (JSON or Console)
            → stdout / file
    """
    settings = get_settings()

    # ------------------------------------------------------------------
    # Shared processor chain
    # Applied to ALL log records regardless of renderer.
    # ------------------------------------------------------------------
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,          # Inject request-scoped context
        structlog.stdlib.add_logger_name,                 # Add logger name (module path)
        structlog.stdlib.add_log_level,                   # Add log level string
        structlog.stdlib.PositionalArgumentsFormatter(),  # Handle %s-style formatting
        structlog.processors.TimeStamper(fmt="iso"),      # ISO 8601 timestamps
        _drop_color_message_key,                          # Remove uvicorn color noise
        _add_app_context,                                 # Inject app metadata
        structlog.processors.StackInfoRenderer(),         # Render stack_info
        structlog.processors.format_exc_info,             # Format exception tracebacks
        structlog.processors.UnicodeDecoder(),            # Decode bytes to strings
    ]

    # ------------------------------------------------------------------
    # Choose renderer based on configured log format
    # ------------------------------------------------------------------
    if settings.LOG_FORMAT == "json":
        renderer: Any = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    # ------------------------------------------------------------------
    # Configure structlog
    # ------------------------------------------------------------------
    structlog.configure(
        processors=shared_processors
        + [
            # Bridge: converts structlog events to stdlib LogRecord objects
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # ------------------------------------------------------------------
    # Configure stdlib formatter using structlog's bridge
    # ------------------------------------------------------------------
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # ------------------------------------------------------------------
    # Attach handler(s) to the root stdlib logger
    # ------------------------------------------------------------------
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.LOG_LEVEL.upper())

    # Optional file handler
    if settings.LOG_FILE_PATH:
        file_handler = logging.FileHandler(settings.LOG_FILE_PATH, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # ------------------------------------------------------------------
    # Silence noisy third-party loggers in non-debug mode
    # ------------------------------------------------------------------
    if not settings.DEBUG:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("alembic").setLevel(logging.INFO)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Return a structlog bound logger for the given name.

    Usage::

        from app.core.logging import get_logger

        logger = get_logger(__name__)
        logger.info("Event occurred", key="value")

    Args:
        name: Logger name, typically ``__name__``. Defaults to root logger.

    Returns:
        A structlog BoundLogger instance.
    """
    return structlog.get_logger(name)
