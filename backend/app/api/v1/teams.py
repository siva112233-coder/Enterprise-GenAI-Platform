"""
API route handlers for Team management.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.utils import handle_domain_exception
from app.dependencies.common import DBSession
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.team import TeamCreate, TeamResponse, TeamUpdate
from app.security.dependencies import get_current_user, require_role
from app.services.team import TeamService

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[TeamResponse],
    status_code=status.HTTP_200_OK,
    summary="List teams",
    description=(
        "Fetch a paginated, searchable, sorted list of all teams, "
        "optionally filtered by organization."
    ),
)
async def list_teams(
    db: DBSession,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None, description="Search term for team name"),
    organization_id: uuid.UUID | None = Query(None, description="Filter by parent organization ID"),
    sort_by: str | None = Query(None, description="Field to sort by (e.g. name, created_at)"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[TeamResponse]:
    """Fetch paginated teams list."""
    service = TeamService(db)
    items, total = await service.list_teams(
        limit=limit,
        offset=offset,
        search=search,
        organization_id=organization_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    items_out = [TeamResponse.model_validate(item) for item in items]
    return PaginatedResponse(items=items_out, total=total, limit=limit, offset=offset)


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    summary="Get team",
    description="Retrieve details for a single team.",
)
async def get_team(
    team_id: uuid.UUID,
    db: DBSession,
    current_user: User = Depends(get_current_user),
) -> TeamResponse:
    """Retrieve single team context."""
    service = TeamService(db)
    try:
        team = await service.get_team_by_id(team_id)
        return TeamResponse.model_validate(team)
    except Exception as exc:
        handle_domain_exception(exc)
        raise


@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create team",
    description="Create a new working group team inside an organization. Restricted to ADMIN.",
)
async def create_team(
    team_in: TeamCreate,
    db: DBSession,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> TeamResponse:
    """Register a new team."""
    service = TeamService(db)
    try:
        team = await service.create_team(team_in)
        return TeamResponse.model_validate(team)
    except Exception as exc:
        handle_domain_exception(exc)
        raise


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    summary="Update team",
    description="Update fields on an existing team. Restricted to ADMIN.",
)
async def update_team(
    team_id: uuid.UUID,
    team_in: TeamUpdate,
    db: DBSession,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> TeamResponse:
    """Modify team fields."""
    service = TeamService(db)
    try:
        team = await service.update_team(team_id, team_in)
        return TeamResponse.model_validate(team)
    except Exception as exc:
        handle_domain_exception(exc)
        raise


@router.delete(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete team",
    description="Purge a team from the system. Restricted to ADMIN.",
)
async def delete_team(
    team_id: uuid.UUID,
    db: DBSession,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> TeamResponse:
    """Delete a team."""
    service = TeamService(db)
    try:
        team = await service.delete_team(team_id)
        return TeamResponse.model_validate(team)
    except Exception as exc:
        handle_domain_exception(exc)
        raise
