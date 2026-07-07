"""
Utility helper functions for API route handlers in v1.
"""

from fastapi import HTTPException, status

from app.utils.exceptions import (
    DuplicateResourceError,
    ForbiddenError,
    ResourceNotFoundError,
    ValidationError,
)


def handle_domain_exception(exc: Exception) -> None:
    """
    Catch a domain-specific exception and translate it into a FastAPI HTTPException.

    Args:
        exc: The caught domain error.

    Raises:
        HTTPException: The corresponding HTTP transport error.
    """
    if isinstance(exc, ResourceNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    if isinstance(exc, DuplicateResourceError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message)
    if isinstance(exc, ForbiddenError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    raise exc
