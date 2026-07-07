"""
API route handlers for user registration, authentication, token refresh, and profile fetching.
"""

from fastapi import APIRouter, Depends, status

from app.dependencies.common import DBSession
from app.models.user import User
from app.schemas.auth import (
    TokenRefreshRequest,
    TokenResponse,
    UserLogin,
    UserMeResponse,
    UserRegister,
)
from app.schemas.user import UserResponse
from app.security.auth_service import AuthService
from app.security.dependencies import get_current_user

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Create a new user profile. Resolves or generates the organization "
        "and team matching the request inputs."
    ),
)
async def register(user_in: UserRegister, db: DBSession) -> User:
    """Register a user and resolve organization and team constraints."""
    auth_service = AuthService(db)
    return await auth_service.register_user(user_in)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Log in user",
    description=(
        "Verify credentials and return a token payload containing "
        "access and refresh tokens."
    ),
)
async def login(login_in: UserLogin, db: DBSession) -> TokenResponse:
    """Login flow issuing Bearer token pairs."""
    auth_service = AuthService(db)
    return await auth_service.login_user(login_in)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh session tokens",
    description=(
        "Provide a valid refresh token to obtain a fresh pair of "
        "access and refresh tokens."
    ),
)
async def refresh(refresh_in: TokenRefreshRequest, db: DBSession) -> TokenResponse:
    """Exchange refresh token for updated access/refresh pair."""
    auth_service = AuthService(db)
    return await auth_service.refresh_session(refresh_in)


@router.get(
    "/me",
    response_model=UserMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Fetch full entity details for the currently active, authenticated user session.",
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserMeResponse:
    """Retrieve current user context with team and organization values."""
    return UserMeResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        status=current_user.status,
        team_id=current_user.team.id,
        team_name=current_user.team.name,
        organization_id=current_user.team.organization.id,
        organization_name=current_user.team.organization.name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
