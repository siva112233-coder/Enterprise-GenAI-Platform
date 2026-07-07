"""Repository module handling database operations for User models."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.team import Team
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository handling database access for User models."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=User, db=db)

    async def list_paginated(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        search: str | None = None,
        team_id: uuid.UUID | None = None,
        organization_id: uuid.UUID | None = None,
        role: str | None = None,
        status: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[User], int]:
        """
        List users with pagination, filtering, search, and sorting.

        Args:
            limit: Maximum records to return.
            offset: Records to skip.
            search: Optional text search on name or email.
            team_id: Optional team filter.
            organization_id: Optional organization filter.
            role: Optional role filter.
            status: Optional status filter.
            sort_by: Attribute name to sort by.
            sort_order: 'asc' or 'desc'.

        Returns:
            tuple: (List of User instances, total count).
        """
        stmt = select(self.model)

        if organization_id:
            stmt = stmt.join(Team, self.model.team_id == Team.id).where(
                Team.organization_id == organization_id
            )
        if team_id:
            stmt = stmt.where(self.model.team_id == team_id)
        if role:
            stmt = stmt.where(self.model.role == role)
        if status:
            stmt = stmt.where(self.model.status == status)
        if search:
            stmt = stmt.where(
                self.model.full_name.ilike(f"%{search}%") | self.model.email.ilike(f"%{search}%")
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        if sort_by and hasattr(self.model, sort_by):
            col = getattr(self.model, sort_by)
            stmt = stmt.order_by(col.desc() if sort_order == "desc" else col.asc())
        else:
            stmt = stmt.order_by(self.model.email.asc())

        stmt = stmt.options(selectinload(self.model.team).selectinload(Team.organization))
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

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

    async def get_by_email_with_relations(self, email: str) -> User | None:
        """
        Retrieve a user by email, eagerly loading team and organization relations.

        Args:
            email: The email address of the user.

        Returns:
            The User model instance or None.
        """
        result = await self.db.execute(
            select(self.model)
            .where(self.model.email == email)
            .options(
                selectinload(self.model.team)
                .selectinload(Team.organization)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(self, id: uuid.UUID) -> User | None:
        """
        Retrieve a user by ID, eagerly loading team and organization relations.

        Args:
            id: The primary key ID of the user.

        Returns:
            The User model instance or None.
        """
        result = await self.db.execute(
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(self.model.team)
                .selectinload(Team.organization)
            )
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
