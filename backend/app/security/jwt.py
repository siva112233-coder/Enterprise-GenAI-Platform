"""
JWT utility functions for issuing, verifying, and decoding access and refresh tokens.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.core.config import get_settings


def create_access_token(
    subject: str | uuid.UUID, expires_delta: timedelta | None = None
) -> str:
    """
    Generate an access token with a specified subject.

    Args:
        subject: The subject of the token (typically user ID).
        expires_delta: Optional custom expiration time delta.

    Returns:
        str: Encoded JWT access token.
    """
    settings = get_settings()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.now(UTC),
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str | uuid.UUID, expires_delta: timedelta | None = None
) -> str:
    """
    Generate a refresh token with a specified subject.

    Args:
        subject: The subject of the token (typically user ID).
        expires_delta: Optional custom expiration time delta.

    Returns:
        str: Encoded JWT refresh token.
    """
    settings = get_settings()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.now(UTC),
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT.

    Raises PyJWT exceptions (e.g. ExpiredSignatureError, InvalidTokenError)
    if the token is invalid or expired.

    Args:
        token: The encoded JWT token string.

    Returns:
        dict[str, Any]: Decoded payload claims.
    """
    settings = get_settings()
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
