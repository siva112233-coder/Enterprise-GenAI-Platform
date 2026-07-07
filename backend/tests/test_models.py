import pytest
from datetime import datetime
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import models to register them on Base.metadata
import app.models
from app.models.organization import Organization
from app.models.team import Team
from app.models.user import User
from app.models.application import Application
from app.models.enums import UserRole, UserStatus


@pytest.mark.asyncio
async def test_create_organization(db_session: AsyncSession):
    """Test creating an organization model."""
    org = Organization(name="Acme Corp", slug="acme")
    db_session.add(org)
    await db_session.flush()

    assert org.id is not None
    assert isinstance(org.id, uuid.UUID)
    assert org.name == "Acme Corp"
    assert org.slug == "acme"
    assert isinstance(org.created_at, datetime)
    assert isinstance(org.updated_at, datetime)


@pytest.mark.asyncio
async def test_organization_team_relationship(db_session: AsyncSession):
    """Test Organization-to-Team one-to-many relationship."""
    org = Organization(name="Acme Corp", slug="acme")
    db_session.add(org)
    await db_session.flush()

    team = Team(name="Engineering", organization_id=org.id)
    db_session.add(team)
    await db_session.flush()

    # Query organization with teams eagerly loaded
    from sqlalchemy.orm import selectinload
    result = await db_session.execute(
        select(Organization).options(selectinload(Organization.teams)).where(Organization.id == org.id)
    )
    db_org = result.scalar_one()
    assert len(db_org.teams) == 1
    assert db_org.teams[0].name == "Engineering"


@pytest.mark.asyncio
async def test_cascade_delete(db_session: AsyncSession):
    """Test cascade deletion from Organization down to Team, User, and Application."""
    # 1. Create Organization
    org = Organization(name="Acme Corp", slug="acme")
    db_session.add(org)
    await db_session.flush()

    # 2. Create Team
    team = Team(name="Engineering", organization_id=org.id)
    db_session.add(team)
    await db_session.flush()

    # 3. Create User
    user = User(
        email="dev@acme.com",
        full_name="Acme Dev",
        role=UserRole.DEVELOPER,
        status=UserStatus.ACTIVE,
        team_id=team.id,
    )
    db_session.add(user)

    # 4. Create Application
    app = Application(
        name="Gateway App",
        description="GenAI client",
        team_id=team.id,
    )
    db_session.add(app)
    await db_session.flush()

    # Verify everything exists
    assert (await db_session.get(Organization, org.id)) is not None
    assert (await db_session.get(Team, team.id)) is not None
    assert (await db_session.get(User, user.id)) is not None
    assert (await db_session.get(Application, app.id)) is not None

    # Delete organization
    await db_session.delete(org)
    await db_session.flush()

    # Verify cascading deletes
    assert (await db_session.get(Organization, org.id)) is None
    assert (await db_session.get(Team, team.id)) is None
    assert (await db_session.get(User, user.id)) is None
    assert (await db_session.get(Application, app.id)) is None
