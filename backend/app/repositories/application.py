import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.models.team import Team
from app.repositories.base import BaseRepository
from app.schemas.application import ApplicationCreate, ApplicationUpdate


class ApplicationRepository(BaseRepository[Application, ApplicationCreate, ApplicationUpdate]):
    """Repository handling database access for Application models."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=Application, db=db)

    async def get_by_name_and_team(self, name: str, team_id: uuid.UUID) -> Application | None:
        """Retrieve an application by name and team."""
        result = await self.db.execute(
            select(self.model).where(self.model.name == name, self.model.team_id == team_id)
        )
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        search: str | None = None,
        team_id: uuid.UUID | None = None,
        is_active: bool | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[Application], int]:
        """
        List applications with pagination, filtering, search, and sorting.

        Args:
            limit: Maximum records to return.
            offset: Records to skip.
            search: Optional text search on application name.
            team_id: Optional team filter.
            is_active: Optional activity status filter.
            sort_by: Attribute name to sort by.
            sort_order: 'asc' or 'desc'.

        Returns:
            tuple: (List of Application instances, total count).
        """
        stmt = select(self.model)
        if team_id:
            stmt = stmt.where(self.model.team_id == team_id)
        if is_active is not None:
            stmt = stmt.where(self.model.is_active == is_active)
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

        # Eagerly load the team relation
        stmt = stmt.options(selectinload(self.model.team).selectinload(Team.organization))

        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

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
