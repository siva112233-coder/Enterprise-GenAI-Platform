import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository handling database access for User models."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=User, db=db)

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their unique email address.

        Args:
            email: The email address of the user.

        Returns:
            The User model instance or None.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()

    async def get_users_by_team(self, team_id: uuid.UUID) -> list[User]:
        """
        Retrieve all users belonging to a specific team.

        Args:
            team_id: The team ID.

        Returns:
            A list of User model instances.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.team_id == team_id)
        )
        return list(result.scalars().all())

    async def get_users_by_organization(self, organization_id: uuid.UUID) -> list[User]:
        """
        Retrieve all users belonging to any team under a specific organization.

        Args:
            organization_id: The organization ID.

        Returns:
            A list of User model instances.
        """
        result = await self.db.execute(
            select(self.model)
            .join(Team, self.model.team_id == Team.id)
            .where(Team.organization_id == organization_id)
        )
        return list(result.scalars().all())
