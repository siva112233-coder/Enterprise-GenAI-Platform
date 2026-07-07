from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.repositories.base import BaseRepository
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class OrganizationRepository(BaseRepository[Organization, OrganizationCreate, OrganizationUpdate]):
    """Repository handling database access for Organization models."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=Organization, db=db)

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
