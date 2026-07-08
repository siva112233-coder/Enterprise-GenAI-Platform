"""
Custom exception types for the AI Gateway.

Re-exports all gateway exceptions for convenient single-import access::

    from app.exceptions import ProviderNotFound, ProviderUnavailable
"""

from app.exceptions.gateway import (
    GatewayException,
    InvalidModel,
    ProviderNotFound,
    ProviderUnavailable,
    RequestValidationError,
)

__all__ = [
    "GatewayException",
    "InvalidModel",
    "ProviderNotFound",
    "ProviderUnavailable",
    "RequestValidationError",
]
