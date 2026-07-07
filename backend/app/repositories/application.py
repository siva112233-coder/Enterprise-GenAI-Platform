import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.team import Team
from app.repositories.base import BaseRepository
from app.schemas.application import ApplicationCreate, ApplicationUpdate


class ApplicationRepository(BaseRepository[Application, ApplicationCreate, ApplicationUpdate]):
    """Repository handling database access for Application models."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=Application, db=db)

    async def get_applications_by_team(self, team_id: uuid.UUID) -> list[Application]:
        """
        Retrieve all applications belonging to a specific team.

        Args:
            team_id: The team ID.

        Returns:
            A list of Application model instances.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.team_id == team_id)
        )
        return list(result.scalars().all())

    async def get_applications_by_organization(
        self, organization_id: uuid.UUID
    ) -> list[Application]:
        """
        Retrieve all applications belonging to any team under a specific organization.

        Args:
            organization_id: The organization ID.

        Returns:
            A list of Application model instances.
        """
        result = await self.db.execute(
            select(self.model)
            .join(Team, self.model.team_id == Team.id)
            .where(Team.organization_id == organization_id)
        )
        return list(result.scalars().all())
