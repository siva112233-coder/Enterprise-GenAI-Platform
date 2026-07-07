"""
FastAPI dependencies for handling JWT authentication and role-based access control.
"""

import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError

from app.core.config import get_settings
from app.dependencies.common import DBSession
from app.models.enums import UserRole, UserStatus
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security.jwt import decode_token

settings = get_settings()

# Define the OAuth2 security scheme.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    description="Provide the JWT access token in the Authorization header as Bearer token.",
)


async def get_current_user(
    db: DBSession,
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    FastAPI dependency to retrieve the currently logged-in and authenticated user.

    Eagerly loads the user's team and organization.

    Args:
        db: The active database async session.
        token: The bearer JWT token.

    Returns:
        User: The authenticated User ORM model.

    Raises:
        HTTPException: 401 if token validation fails, 403 if user account is restricted.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception

        sub = payload.get("sub")
        if not sub:
            raise credentials_exception

        user_id = uuid.UUID(sub)
    except (PyJWTError, ValueError) as exc:
        raise credentials_exception from exc

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id_with_relations(user_id)
    if not user:
        raise credentials_exception

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is currently inactive or suspended.",
        )

    return user


def require_role(allowed_roles: list[UserRole] | UserRole) -> Callable[[User], User]:
    """
    FastAPI dependency factory enforcing role-based access control (RBAC).

    Args:
        allowed_roles: A list of allowed roles or a single allowed role.

    Returns:
        Callable: Dependency guard requiring current user to have one of the roles.
    """
    roles_list = [allowed_roles] if isinstance(allowed_roles, UserRole) else allowed_roles

    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles_list:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required permissions to perform this action.",
            )
        return current_user

    return role_dependency
