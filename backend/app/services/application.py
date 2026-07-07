"""
Service class coordinating business rules for Application management.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.models.application import Application
from app.models.team import Team
from app.repositories.application import ApplicationRepository
from app.repositories.team import TeamRepository
from app.schemas.application import ApplicationCreate, ApplicationUpdate
from app.utils.exceptions import DuplicateResourceError, ResourceNotFoundError

logger = get_logger(__name__)


class ApplicationService:
    """Service layer executing business rules on Application entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.app_repo = ApplicationRepository(db)
        self.team_repo = TeamRepository(db)

    async def get_app_by_id(self, app_id: uuid.UUID) -> Application:
        """Retrieve an application or raise ResourceNotFoundError."""
        app = await self.app_repo.get_by_id(app_id)
        if not app:
            logger.warning("Application not found", app_id=str(app_id))
            raise ResourceNotFoundError(f"Application with ID {app_id} not found.")
        return app

    async def list_apps(
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
        """Fetch a paginated list of applications."""
        return await self.app_repo.list_paginated(
            limit=limit,
            offset=offset,
            search=search,
            team_id=team_id,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def create_app(self, app_in: ApplicationCreate) -> Application:
        """Create a new application, ensuring owner team exists and name is unique per team."""
        log = logger.bind(name=app_in.name, team_id=str(app_in.team_id))
        log.info("Creating application")

        # 1. Ensure team exists
        team = await self.team_repo.get_by_id(app_in.team_id)
        if not team:
            log.warning("Failed to create application: owner team does not exist")
            raise ResourceNotFoundError(f"Team with ID {app_in.team_id} does not exist.")

        # 2. Ensure application name is unique inside the team
        existing = await self.app_repo.get_by_name_and_team(app_in.name, app_in.team_id)
        if existing:
            log.warning("Failed to create application: name already exists in team")
            raise DuplicateResourceError(
                f"Application with name '{app_in.name}' already exists in this team."
            )

        app = await self.app_repo.create(app_in)
        await self.db.flush()

        # Eager load relationships for responses
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        stmt = select(Application).where(Application.id == app.id).options(
            selectinload(Application.team).selectinload(Team.organization)
        )
        app_with_relations = (await self.db.execute(stmt)).scalar_one()

        log.info("Application created", app_id=str(app.id))
        return app_with_relations

    async def update_app(self, app_id: uuid.UUID, app_in: ApplicationUpdate) -> Application:
        """Update application details verifying uniqueness and team constraints."""
        log = logger.bind(app_id=str(app_id))
        log.info("Updating application")

        app = await self.get_app_by_id(app_id)

        target_team_id = app_in.team_id or app.team_id

        # If team is changing, verify the target team exists
        if app_in.team_id and app_in.team_id != app.team_id:
            team = await self.team_repo.get_by_id(app_in.team_id)
            if not team:
                log.warning("Failed to update application: target team does not exist")
                raise ResourceNotFoundError(f"Team with ID {app_in.team_id} does not exist.")

        # Check unique constraint if name is changing (or if team is changing)
        if (app_in.name and app_in.name != app.name) or (
            app_in.team_id and app_in.team_id != app.team_id
        ):
            name_to_check = app_in.name or app.name
            existing = await self.app_repo.get_by_name_and_team(name_to_check, target_team_id)
            if existing and existing.id != app.id:
                log.warning("Failed to update application: name already exists in target team")
                raise DuplicateResourceError(
                    f"Application with name '{name_to_check}' already exists in the target team."
                )

        updated_app = await self.app_repo.update(app, app_in)
        await self.db.flush()

        # Eager load relationships for responses
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        stmt = select(Application).where(Application.id == updated_app.id).options(
            selectinload(Application.team).selectinload(Team.organization)
        )
        app_with_relations = (await self.db.execute(stmt)).scalar_one()

        log.info("Application updated")
        return app_with_relations

    async def delete_app(self, app_id: uuid.UUID) -> Application:
        """Delete application by ID."""
        log = logger.bind(app_id=str(app_id))
        log.info("Deleting application")

        app = await self.get_app_by_id(app_id)
        await self.app_repo.delete(app_id)
        await self.db.flush()
        log.info("Application deleted")
        return app
