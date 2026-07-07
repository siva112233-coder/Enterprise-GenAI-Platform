"""
Password hashing and verification utilities for the Enterprise GenAI Platform.
"""

from passlib.context import CryptContext

# Set up the CryptContext to use bcrypt as the primary hashing algorithm.
# Deprecated "auto" will handle any legacy hash upgrades if required.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password: The raw plaintext password to hash.

    Returns:
        str: The bcrypt-hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its bcrypt hash.

    Args:
        plain_password: The raw plaintext password to verify.
        hashed_password: The bcrypt hash to verify against.

    Returns:
        bool: True if password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
