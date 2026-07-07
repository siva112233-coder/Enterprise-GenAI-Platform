"""
Service class coordinating business rules for User management.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.models.enums import UserRole
from app.models.user import User
from app.repositories.team import TeamRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.security.password import hash_password
from app.utils.exceptions import (
    DuplicateResourceError,
    ForbiddenError,
    ResourceNotFoundError,
)

logger = get_logger(__name__)


class UserService:
    """Service layer executing business rules on User entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.team_repo = TeamRepository(db)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        """Retrieve a user or raise ResourceNotFoundError."""
        user = await self.user_repo.get_by_id_with_relations(user_id)
        if not user:
            logger.warning("User not found", user_id=str(user_id))
            raise ResourceNotFoundError(f"User with ID {user_id} not found.")
        return user

    async def list_users(
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
        """Fetch a paginated list of users."""
        return await self.user_repo.list_paginated(
            limit=limit,
            offset=offset,
            search=search,
            team_id=team_id,
            organization_id=organization_id,
            role=role,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def create_user(self, user_in: UserCreate) -> User:
        """Create a new user entity with password hashing and team verification."""
        log = logger.bind(email=user_in.email, role=user_in.role)
        log.info("Creating user")

        # 1. Verify email uniqueness
        existing = await self.user_repo.get_by_email(user_in.email)
        if existing:
            log.warning("Failed to create user: email already exists")
            raise DuplicateResourceError(f"Email '{user_in.email}' is already registered.")

        # 2. Verify parent team exists
        team = await self.team_repo.get_by_id(user_in.team_id)
        if not team:
            log.warning("Failed to create user: owner team does not exist")
            raise ResourceNotFoundError(f"Team with ID {user_in.team_id} does not exist.")

        # 3. Hash password
        hashed_pwd = hash_password(user_in.password or "temporary_default_pass_123")

        # Create user
        user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            role=user_in.role,
            status=user_in.status,
            hashed_password=hashed_pwd,
            team_id=user_in.team_id,
        )

        self.db.add(user)
        await self.db.flush()

        # Load relation models for responses
        user_with_relations = await self.get_user_by_id(user.id)
        log.info("User created", user_id=str(user.id))
        return user_with_relations

    async def update_user(
        self, user_id: uuid.UUID, user_in: UserUpdate, current_user: User
    ) -> User:
        """
        Update user profile.

        Restricts non-admins to only updating their own profile and restricts
        what fields they can modify.
        """
        log = logger.bind(target_user_id=str(user_id), current_user_id=str(current_user.id))
        log.info("Updating user profile")

        # Retrieve target user
        user = await self.get_user_by_id(user_id)

        # 1. Enforce Role-based authorization constraints
        if current_user.role != UserRole.ADMIN:
            # Non-admins can only update their own profile
            if user.id != current_user.id:
                log.warning("Unauthorized profile update attempt")
                raise ForbiddenError("You can only update your own profile.")

            # Non-admins cannot elevate their role, status, or modify their team
            if (
                (user_in.role and user_in.role != user.role)
                or (user_in.status and user_in.status != user.status)
                or (user_in.team_id and user_in.team_id != user.team_id)
            ):
                log.warning("Restricted profile modification attempt")
                raise ForbiddenError(
                    "You do not have permission to modify your role, status, or team."
                )

        # 2. Check email uniqueness if email is changing
        if user_in.email and user_in.email != user.email:
            existing = await self.user_repo.get_by_email(user_in.email)
            if existing:
                log.warning("Failed to update user: email already exists")
                raise DuplicateResourceError(f"Email '{user_in.email}' is already registered.")

        # 3. Verify target team exists if changing
        if user_in.team_id and user_in.team_id != user.team_id:
            team = await self.team_repo.get_by_id(user_in.team_id)
            if not team:
                log.warning("Failed to update user: target team does not exist")
                raise ResourceNotFoundError(f"Team with ID {user_in.team_id} does not exist.")

        # Convert schema to dict for updating
        update_data = user_in.model_dump(exclude_unset=True)

        # Hash password if provided
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        elif "password" in update_data:
            update_data.pop("password")  # Ignore empty password fields

        # Apply updates
        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.add(user)
        await self.db.flush()

        # Eagerly load relationships
        user_with_relations = await self.get_user_by_id(user.id)
        log.info("User profile updated")
        return user_with_relations

    async def delete_user(self, user_id: uuid.UUID) -> User:
        """Delete user by ID."""
        log = logger.bind(user_id=str(user_id))
        log.info("Deleting user")

        user = await self.get_user_by_id(user_id)
        await self.user_repo.delete(user_id)
        await self.db.flush()
        log.info("User deleted")
        return user
