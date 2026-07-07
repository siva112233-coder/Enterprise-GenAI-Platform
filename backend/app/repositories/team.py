import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.repositories.base import BaseRepository
from app.schemas.team import TeamCreate, TeamUpdate


class TeamRepository(BaseRepository[Team, TeamCreate, TeamUpdate]):
    """Repository handling database access for Team models."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=Team, db=db)

    async def get_teams_by_organization(self, organization_id: uuid.UUID) -> list[Team]:
        """
        Retrieve all teams belonging to a specific organization.

        Args:
            organization_id: The ID of the organization.

        Returns:
            A list of Team models.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.organization_id == organization_id)
        )
        return list(result.scalars().all())
