"""
Generic pagination schemas for the Enterprise GenAI Platform.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response structure wrapping data list with offset metadata."""

    items: list[T]
    total: int
    limit: int
    offset: int
