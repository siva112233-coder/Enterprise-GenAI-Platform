"""
Structured logging configuration for the AI Gateway.

Uses structlog for JSON-structured log output in production
and colourised console output in development/debug mode.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from app.core.config import settings


def _add_service_context(
    logger: Any,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Inject service name and version into every log record."""
    event_dict["service"] = settings.SERVICE_NAME
    event_dict["version"] = settings.SERVICE_VERSION
    event_dict["environment"] = settings.ENVIRONMENT
    return event_dict


def configure_logging() -> None:
    """
    Configure structlog and the stdlib logging bridge.

    Call once at application startup (inside the lifespan handler).
    After this call, any code that calls ``structlog.get_logger()``
    will emit structured log events.
    """
    log_level_int = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # ── Shared processors (applied before the final renderer) ─────────────────
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_service_context,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # ── Choose renderer based on LOG_FORMAT setting ───────────────────────────
    if settings.LOG_FORMAT.lower() == "json":
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level_int),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # ── Bridge stdlib logging → structlog ─────────────────────────────────────
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level_int,
    )

    # Suppress noisy third-party loggers
    for noisy in ("uvicorn.access", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str = "gateway") -> structlog.BoundLogger:
    """
    Return a bound structlog logger.

    Usage::

        logger = get_logger(__name__)
        logger.info("provider_called", provider="openai", model="gpt-4o")
    """
    return structlog.get_logger(name)
