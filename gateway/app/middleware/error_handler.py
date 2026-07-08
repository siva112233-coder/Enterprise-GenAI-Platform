"""
Global error-handler middleware for the AI Gateway.

Maps all exception types to structured JSON error responses
with appropriate HTTP status codes and machine-readable error codes.

Separation of concerns: route handlers raise domain exceptions;
this middleware is the single translation point to HTTP responses.
"""

from __future__ import annotations

from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import get_logger
from app.exceptions.gateway import GatewayException
from shared.exceptions import BasePlatformException

logger = get_logger("gateway.middleware.error_handler")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Catches all unhandled exceptions and returns a structured JSON error.

    Hierarchy:
      1. ``GatewayException`` (and subclasses) → HTTP status from exception
      2. ``BasePlatformException`` → HTTP status from exception
      3. ``pydantic.ValidationError`` → 422
      4. ``NotImplementedError`` → 501 (provider not yet integrated)
      5. All other exceptions → 500
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)

        except GatewayException as exc:
            logger.warning(
                "gateway.exception",
                code=exc.code,
                message=exc.message,
                status_code=exc.status_code,
                path=request.url.path,
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                    }
                },
            )

        except BasePlatformException as exc:
            logger.warning(
                "platform.exception",
                code=exc.code,
                message=exc.message,
                status_code=exc.status_code,
                path=request.url.path,
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                    }
                },
            )

        except ValidationError as exc:
            logger.warning(
                "validation.error",
                errors=exc.errors(),
                path=request.url.path,
            )
            return JSONResponse(
                status_code=422,
                content={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Request body failed schema validation.",
                        "detail": exc.errors(),
                    }
                },
            )

        except NotImplementedError as exc:
            logger.warning(
                "provider.not_implemented",
                message=str(exc),
                path=request.url.path,
            )
            return JSONResponse(
                status_code=501,
                content={
                    "error": {
                        "code": "NOT_IMPLEMENTED",
                        "message": (
                            "This provider's API integration has not been "
                            "implemented yet. See provider TODO comments."
                        ),
                        "detail": str(exc),
                    }
                },
            )

        except Exception as exc:
            logger.exception(
                "gateway.unhandled_exception",
                exc_info=exc,
                path=request.url.path,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred in the gateway.",
                    }
                },
            )
