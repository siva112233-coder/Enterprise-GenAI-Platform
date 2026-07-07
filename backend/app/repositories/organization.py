from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.repositories.base import BaseRepository
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class OrganizationRepository(BaseRepository[Organization, OrganizationCreate, OrganizationUpdate]):
    """Repository handling database access for Organization models."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=Organization, db=db)

    async def list_paginated(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[Organization], int]:
        """
        List organizations with pagination, search, and sorting.

        Args:
            limit: Maximum records to return.
            offset: Records to skip.
            search: Optional text search on organization name.
            sort_by: Attribute name to sort by.
            sort_order: 'asc' or 'desc'.

        Returns:
            tuple: (List of Organization instances, total count).
        """
        stmt = select(self.model)
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

    async def get_by_slug(self, slug: str) -> Organization | None:
        """
        Retrieve an organization by its unique URL slug.

        Args:
            slug: The organization slug.

        Returns:
            The Organization model instance or None.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Organization | None:
        """
        Retrieve an organization by its name.

        Args:
            name: The organization name.

        Returns:
            The Organization model instance or None.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.name == name)
        )
        return result.scalar_one_or_none()
