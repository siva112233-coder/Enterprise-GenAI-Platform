"""
Service class coordinating business rules for Organization management.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.models.organization import Organization
from app.repositories.organization import OrganizationRepository
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.utils.exceptions import DuplicateResourceError, ResourceNotFoundError

logger = get_logger(__name__)


class OrganizationService:
    """Service layer executing business rules on Organization entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.org_repo = OrganizationRepository(db)

    async def get_org_by_id(self, org_id: uuid.UUID) -> Organization:
        """Retrieve an organization or raise ResourceNotFoundError."""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            logger.warning("Organization not found", org_id=str(org_id))
            raise ResourceNotFoundError(f"Organization with ID {org_id} not found.")
        return org

    async def list_orgs(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[Organization], int]:
        """Fetch a paginated list of organizations."""
        return await self.org_repo.list_paginated(
            limit=limit,
            offset=offset,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def create_org(self, org_in: OrganizationCreate) -> Organization:
        """Create a new organization checking for unique constraints on name/slug."""
        log = logger.bind(name=org_in.name, slug=org_in.slug)
        log.info("Creating organization")

        # Check unique constraint
        existing_name = await self.org_repo.get_by_name(org_in.name)
        if existing_name:
            log.warning("Failed to create organization: name already exists")
            raise DuplicateResourceError(
                f"Organization name '{org_in.name}' is already in use."
            )

        existing_slug = await self.org_repo.get_by_slug(org_in.slug)
        if existing_slug:
            log.warning("Failed to create organization: slug already exists")
            raise DuplicateResourceError(
                f"Organization slug '{org_in.slug}' is already in use."
            )

        org = await self.org_repo.create(org_in)
        await self.db.flush()
        log.info("Organization created", org_id=str(org.id))
        return org

    async def update_org(self, org_id: uuid.UUID, org_in: OrganizationUpdate) -> Organization:
        """Update organization details ensuring unique constraints are maintained."""
        log = logger.bind(org_id=str(org_id))
        log.info("Updating organization")

        org = await self.get_org_by_id(org_id)

        # Validate unique constraints if name is changing
        if org_in.name and org_in.name != org.name:
            existing_name = await self.org_repo.get_by_name(org_in.name)
            if existing_name:
                log.warning("Failed to update organization: name already exists")
                raise DuplicateResourceError(
                    f"Organization name '{org_in.name}' is already in use."
                )

        # Validate unique constraints if slug is changing
        if org_in.slug and org_in.slug != org.slug:
            existing_slug = await self.org_repo.get_by_slug(org_in.slug)
            if existing_slug:
                log.warning("Failed to update organization: slug already exists")
                raise DuplicateResourceError(
                    f"Organization slug '{org_in.slug}' is already in use."
                )

        updated_org = await self.org_repo.update(org, org_in)
        await self.db.flush()
        log.info("Organization updated")
        return updated_org

    async def delete_org(self, org_id: uuid.UUID) -> Organization:
        """Delete organization by ID."""
        log = logger.bind(org_id=str(org_id))
        log.info("Deleting organization")

        org = await self.get_org_by_id(org_id)
        await self.org_repo.delete(org_id)
        await self.db.flush()
        log.info("Organization deleted")
        return org
