"""
Request/Response logging middleware for the AI Gateway.

Injects a structured log entry for every HTTP request, capturing:
  - HTTP method and path
  - Query string (if present)
  - Response status code
  - Wall-clock request duration in milliseconds
  - A per-request correlation ID (X-Request-ID header or generated UUID)

Uses structlog's context-variable support so all log events emitted
*within* a request share the same request_id without explicit passing.
"""

from __future__ import annotations

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

import structlog

from app.core.logging import get_logger

logger = get_logger("gateway.middleware.logging")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that emits one structured log record per request.

    The correlation ID is:
      1. Taken from the inbound ``X-Request-ID`` header, or
      2. Generated as a new UUID4 if not provided.

    The ID is added to the ``X-Request-ID`` response header so clients
    can correlate their requests with gateway logs.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Bind the request_id to structlog's context vars so it appears
        # in all log events emitted during this request's lifecycle.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_ns = time.perf_counter_ns()

        logger.info(
            "http.request",
            method=request.method,
            path=request.url.path,
            query=str(request.url.query) or None,
            client=request.client.host if request.client else None,
        )

        response = await call_next(request)

        duration_ms = (time.perf_counter_ns() - start_ns) / 1_000_000

        logger.info(
            "http.response",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        # Propagate correlation ID to the client
        response.headers["X-Request-ID"] = request_id

        # Clear context vars after the request is fully handled
        structlog.contextvars.clear_contextvars()

        return response
