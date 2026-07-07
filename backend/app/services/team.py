"""
Service class coordinating business rules for Team management.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.models.team import Team
from app.repositories.organization import OrganizationRepository
from app.repositories.team import TeamRepository
from app.schemas.team import TeamCreate, TeamUpdate
from app.utils.exceptions import DuplicateResourceError, ResourceNotFoundError

logger = get_logger(__name__)


class TeamService:
    """Service layer executing business rules on Team entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.team_repo = TeamRepository(db)
        self.org_repo = OrganizationRepository(db)

    async def get_team_by_id(self, team_id: uuid.UUID) -> Team:
        """Retrieve a team or raise ResourceNotFoundError."""
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            logger.warning("Team not found", team_id=str(team_id))
            raise ResourceNotFoundError(f"Team with ID {team_id} not found.")
        return team

    async def list_teams(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        search: str | None = None,
        organization_id: uuid.UUID | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[Team], int]:
        """Fetch a paginated list of teams."""
        return await self.team_repo.list_paginated(
            limit=limit,
            offset=offset,
            search=search,
            organization_id=organization_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def create_team(self, team_in: TeamCreate) -> Team:
        """Create a new team, ensuring parent organization exists and name is unique per org."""
        log = logger.bind(name=team_in.name, org_id=str(team_in.organization_id))
        log.info("Creating team")

        # 1. Ensure Organization exists
        org = await self.org_repo.get_by_id(team_in.organization_id)
        if not org:
            log.warning("Failed to create team: parent organization does not exist")
            raise ResourceNotFoundError(
                f"Organization with ID {team_in.organization_id} does not exist."
            )

        # 2. Ensure team name is unique inside the organization
        existing = await self.team_repo.get_by_name_and_org(team_in.name, team_in.organization_id)
        if existing:
            log.warning("Failed to create team: name already exists in organization")
            raise DuplicateResourceError(
                f"Team with name '{team_in.name}' already exists in this organization."
            )

        team = await self.team_repo.create(team_in)
        await self.db.flush()
        log.info("Team created", team_id=str(team.id))
        return team

    async def update_team(self, team_id: uuid.UUID, team_in: TeamUpdate) -> Team:
        """Update a team, checking for name collisions if changing."""
        log = logger.bind(team_id=str(team_id))
        log.info("Updating team")

        team = await self.get_team_by_id(team_id)

        if team_in.name and team_in.name != team.name:
            existing = await self.team_repo.get_by_name_and_org(
                team_in.name, team.organization_id
            )
            if existing:
                log.warning("Failed to update team: name already exists in organization")
                raise DuplicateResourceError(
                    f"Team with name '{team_in.name}' already exists in this organization."
                )

        updated_team = await self.team_repo.update(team, team_in)
        await self.db.flush()
        log.info("Team updated")
        return updated_team

    async def delete_team(self, team_id: uuid.UUID) -> Team:
        """Delete a team by ID."""
        log = logger.bind(team_id=str(team_id))
        log.info("Deleting team")

        team = await self.get_team_by_id(team_id)
        await self.team_repo.delete(team_id)
        await self.db.flush()
        log.info("Team deleted")
        return team
