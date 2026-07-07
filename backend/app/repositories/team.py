import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.repositories.base import BaseRepository
from app.schemas.team import TeamCreate, TeamUpdate


class TeamRepository(BaseRepository[Team, TeamCreate, TeamUpdate]):
    """Repository handling database access for Team models."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=Team, db=db)

    async def get_by_name_and_org(self, name: str, organization_id: uuid.UUID) -> Team | None:
        """Retrieve a team by name and parent organization."""
        result = await self.db.execute(
            select(self.model).where(
                self.model.name == name, self.model.organization_id == organization_id
            )
        )
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        search: str | None = None,
        organization_id: uuid.UUID | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[Team], int]:
        """
        List teams with pagination, filtering, search, and sorting.

        Args:
            limit: Maximum records to return.
            offset: Records to skip.
            search: Optional text search on team name.
            organization_id: Optional parent organization filter.
            sort_by: Attribute name to sort by.
            sort_order: 'asc' or 'desc'.

        Returns:
            tuple: (List of Team instances, total count).
        """
        stmt = select(self.model)
        if organization_id:
            stmt = stmt.where(self.model.organization_id == organization_id)
        if search:
            stmt = stmt.where(self.model.name.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        if sort_by and hasattr(self.model, sort_by):
            col = getattr(self.model, sort_by)
            stmt = stmt.order_by(col.desc() if sort_order == "desc" else col.asc())
        else:
            stmt = stmt.order_by(self.model.name.asc())

        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

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
