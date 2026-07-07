"""
API route handlers for Application management.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.utils import handle_domain_exception
from app.dependencies.common import DBSession
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
)
from app.schemas.pagination import PaginatedResponse
from app.security.dependencies import get_current_user, require_role
from app.services.application import ApplicationService

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[ApplicationResponse],
    status_code=status.HTTP_200_OK,
    summary="List applications",
    description=(
        "Fetch a paginated, searchable, sorted list of all applications. "
        "Can be filtered by team and activity status."
    ),
)
async def list_applications(
    db: DBSession,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None, description="Search term for application name"),
    team_id: uuid.UUID | None = Query(None, description="Filter by owner team ID"),
    is_active: bool | None = Query(None, description="Filter by application activity status"),
    sort_by: str | None = Query(None, description="Field to sort by (e.g. name, created_at)"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[ApplicationResponse]:
    """Fetch paginated applications list."""
    service = ApplicationService(db)
    items, total = await service.list_apps(
        limit=limit,
        offset=offset,
        search=search,
        team_id=team_id,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    items_out = [ApplicationResponse.model_validate(item) for item in items]
    return PaginatedResponse(items=items_out, total=total, limit=limit, offset=offset)


@router.get(
    "/{app_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get application",
    description="Retrieve details for a single client application.",
)
async def get_application(
    app_id: uuid.UUID,
    db: DBSession,
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    """Retrieve single application context."""
    service = ApplicationService(db)
    try:
        app = await service.get_app_by_id(app_id)
        return ApplicationResponse.model_validate(app)
    except Exception as exc:
        handle_domain_exception(exc)
        raise


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create application",
    description="Register a new client application under a team. Restricted to ADMIN.",
)
async def create_application(
    app_in: ApplicationCreate,
    db: DBSession,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> ApplicationResponse:
    """Register a new client application."""
    service = ApplicationService(db)
    try:
        app = await service.create_app(app_in)
        return ApplicationResponse.model_validate(app)
    except Exception as exc:
        handle_domain_exception(exc)
        raise


@router.put(
    "/{app_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update application",
    description="Update fields on an existing client application. Restricted to ADMIN.",
)
async def update_application(
    app_id: uuid.UUID,
    app_in: ApplicationUpdate,
    db: DBSession,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> ApplicationResponse:
    """Modify client application fields."""
    service = ApplicationService(db)
    try:
        app = await service.update_app(app_id, app_in)
        return ApplicationResponse.model_validate(app)
    except Exception as exc:
        handle_domain_exception(exc)
        raise


@router.delete(
    "/{app_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete application",
    description="Deactivate and delete a client application. Restricted to ADMIN.",
)
async def delete_application(
    app_id: uuid.UUID,
    db: DBSession,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> ApplicationResponse:
    """Delete a client application."""
    service = ApplicationService(db)
    try:
        app = await service.delete_app(app_id)
        return ApplicationResponse.model_validate(app)
    except Exception as exc:
        handle_domain_exception(exc)
        raise
