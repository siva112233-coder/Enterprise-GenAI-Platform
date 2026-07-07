"""
Logging middleware for the Enterprise GenAI Platform.

Intercepts every HTTP request and response to emit structured log records
containing timing, status codes, and request identifiers.

Features:
- Unique ``request_id`` (UUID4) injected into every log record via structlog context vars
- Request duration measured in milliseconds
- Structured fields compatible with log aggregators (Datadog, ELK, GCP Logging)
- Clean context reset after each request (prevents context leakage between requests)

This middleware is mounted BEFORE any route-level logic, ensuring that even
failed or unmatched requests are logged consistently.
"""

import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that logs every HTTP request and response.

    Injects a unique ``request_id`` into the structlog context for the
    duration of each request. This ID is also returned in the response
    headers as ``X-Request-ID`` so it can be correlated with client logs.

    Usage::

        app.add_middleware(RequestLoggingMiddleware)
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request, log metadata, and propagate to the next handler.

        Args:
            request: The incoming HTTP request.
            call_next: The next ASGI handler in the middleware chain.

        Returns:
            Response: The HTTP response from the downstream handler.
        """
        # Generate a unique identifier for this request
        request_id = str(uuid.uuid4())

        # Bind request_id to structlog context vars — all downstream log
        # calls within this request will automatically include this field.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()

        logger.info(
            "Request received",
            method=request.method,
            path=request.url.path,
            query=str(request.url.query) or None,
            client=request.client.host if request.client else None,
        )

        # Process the request
        response: Response = await call_next(request)

        # Calculate duration in milliseconds
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        # Expose request_id in response headers for client-side correlation
        response.headers["X-Request-ID"] = request_id

        # Reset context to prevent leakage into the next request
        structlog.contextvars.clear_contextvars()

        return response
