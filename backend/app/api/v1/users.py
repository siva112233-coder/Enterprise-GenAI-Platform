"""
API route handlers for User management.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.utils import handle_domain_exception
from app.dependencies.common import DBSession
from app.models.enums import UserRole, UserStatus
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.security.dependencies import get_current_user, require_role
from app.services.user import UserService

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List users",
    description=(
        "Fetch a paginated, searchable, sorted list of all users. "
        "Can be filtered by team, organization, role, and status."
    ),
)
async def list_users(
    db: DBSession,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None, description="Search term matching user full name or email"),
    team_id: uuid.UUID | None = Query(None, description="Filter by team ID"),
    organization_id: uuid.UUID | None = Query(None, description="Filter by organization ID"),
    role: UserRole | None = Query(None, description="Filter by user role level"),
    status_filter: UserStatus | None = Query(
        None, alias="status", description="Filter by user status"
    ),
    sort_by: str | None = Query(
        None, description="Field to sort by (e.g. email, full_name, created_at)"
    ),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[UserResponse]:
    """Fetch paginated users list."""
    service = UserService(db)
    items, total = await service.list_users(
        limit=limit,
        offset=offset,
        search=search,
        team_id=team_id,
        organization_id=organization_id,
        role=role.value if role else None,
        status=status_filter.value if status_filter else None,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    items_out = [UserResponse.model_validate(item) for item in items]
    return PaginatedResponse(items=items_out, total=total, limit=limit, offset=offset)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user",
    description="Retrieve details for a single user.",
)
async def get_user(
    user_id: uuid.UUID,
    db: DBSession,
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Retrieve single user context."""
    service = UserService(db)
    try:
        user = await service.get_user_by_id(user_id)
        return UserResponse.model_validate(user)
    except Exception as exc:
        handle_domain_exception(exc)
        raise


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new platform user profile. Restricted to ADMIN.",
)
async def create_user(
    user_in: UserCreate,
    db: DBSession,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> UserResponse:
    """Register a new platform user."""
    service = UserService(db)
    try:
        user = await service.create_user(user_in)
        return UserResponse.model_validate(user)
    except Exception as exc:
        handle_domain_exception(exc)
        raise


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description=(
        "Modify profile fields. ADMIN can update any user's profile. "
        "DEVELOPER can update only their own profile (cannot modify role, status, or team)."
    ),
)
async def update_user(
    user_id: uuid.UUID,
    user_in: UserUpdate,
    db: DBSession,
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Update user profile fields."""
    service = UserService(db)
    try:
        user = await service.update_user(user_id, user_in, current_user)
        return UserResponse.model_validate(user)
    except Exception as exc:
        handle_domain_exception(exc)
        raise


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete user",
    description="Deactivate and purge a user from the database. Restricted to ADMIN.",
)
async def delete_user(
    user_id: uuid.UUID,
    db: DBSession,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> UserResponse:
    """Delete a user profile."""
    service = UserService(db)
    try:
        user = await service.delete_user(user_id)
        return UserResponse.model_validate(user)
    except Exception as exc:
        handle_domain_exception(exc)
        raise
