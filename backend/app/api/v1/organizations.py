"""
API route handlers for Organization management.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.utils import handle_domain_exception
from app.dependencies.common import DBSession
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.schemas.pagination import PaginatedResponse
from app.security.dependencies import get_current_user, require_role
from app.services.organization import OrganizationService

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[OrganizationResponse],
    status_code=status.HTTP_200_OK,
    summary="List organizations",
    description="Fetch a paginated, searchable, sorted list of all organizations.",
)
async def list_organizations(
    db: DBSession,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None, description="Search term for organization name"),
    sort_by: str | None = Query(None, description="Field to sort by (e.g. name, created_at)"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[OrganizationResponse]:
    """Fetch paginated organizations list."""
    service = OrganizationService(db)
    items, total = await service.list_orgs(
        limit=limit,
        offset=offset,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    items_out = [OrganizationResponse.model_validate(item) for item in items]
    return PaginatedResponse(items=items_out, total=total, limit=limit, offset=offset)


@router.get(
    "/{org_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get organization",
    description="Retrieve full details for a single organization.",
)
async def get_organization(
    org_id: uuid.UUID,
    db: DBSession,
    current_user: User = Depends(get_current_user),
) -> OrganizationResponse:
    """Retrieve single organization context."""
    service = OrganizationService(db)
    try:
        org = await service.get_org_by_id(org_id)
        return OrganizationResponse.model_validate(org)
    except Exception as exc:
        handle_domain_exception(exc)
        raise  # Keep compiler happy


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization",
    description="Register a new organization tenant. Restricted to ADMIN.",
)
async def create_organization(
    org_in: OrganizationCreate,
    db: DBSession,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> OrganizationResponse:
    """Create a new organization."""
    service = OrganizationService(db)
    try:
        org = await service.create_org(org_in)
        return OrganizationResponse.model_validate(org)
    except Exception as exc:
        handle_domain_exception(exc)
        raise


@router.put(
    "/{org_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update organization",
    description="Update fields on an existing organization. Restricted to ADMIN.",
)
async def update_organization(
    org_id: uuid.UUID,
    org_in: OrganizationUpdate,
    db: DBSession,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> OrganizationResponse:
    """Modify organization fields."""
    service = OrganizationService(db)
    try:
        org = await service.update_org(org_id, org_in)
        return OrganizationResponse.model_validate(org)
    except Exception as exc:
        handle_domain_exception(exc)
        raise


@router.delete(
    "/{org_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete organization",
    description="Delete an organization tenant. Restricted to ADMIN.",
)
async def delete_organization(
    org_id: uuid.UUID,
    db: DBSession,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> OrganizationResponse:
    """Purge organization entity from storage."""
    service = OrganizationService(db)
    try:
        org = await service.delete_org(org_id)
        return OrganizationResponse.model_validate(org)
    except Exception as exc:
        handle_domain_exception(exc)
        raise
