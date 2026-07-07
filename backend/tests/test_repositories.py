import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

# Import repositories and models
from app.repositories.organization import OrganizationRepository
from app.repositories.team import TeamRepository
from app.repositories.user import UserRepository
from app.repositories.application import ApplicationRepository

from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.schemas.team import TeamCreate, TeamUpdate
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.application import ApplicationCreate, ApplicationUpdate
from app.models.enums import UserRole, UserStatus


@pytest.mark.asyncio
async def test_organization_repository(db_session: AsyncSession):
    """Test CRUD operations on OrganizationRepository."""
    repo = OrganizationRepository(db_session)

    # 1. Create
    org_in = OrganizationCreate(name="Wayne Enterprises", slug="wayne")
    org = await repo.create(org_in)
    assert org.id is not None
    assert org.name == "Wayne Enterprises"

    # 2. Get by ID
    db_org = await repo.get_by_id(org.id)
    assert db_org is not None
    assert db_org.slug == "wayne"

    # 3. Get by slug
    db_org = await repo.get_by_slug("wayne")
    assert db_org is not None
    assert db_org.id == org.id

    # 4. Get by name
    db_org = await repo.get_by_name("Wayne Enterprises")
    assert db_org is not None
    assert db_org.id == org.id

    # 5. List
    orgs = await repo.list()
    assert len(orgs) >= 1

    # 6. Update
    org_up = OrganizationUpdate(name="Wayne Corp")
    updated_org = await repo.update(org, org_up)
    assert updated_org.name == "Wayne Corp"

    # 7. Delete
    await repo.delete(org.id)
    deleted_org = await repo.get_by_id(org.id)
    assert deleted_org is None


@pytest.mark.asyncio
async def test_team_repository(db_session: AsyncSession):
    """Test custom queries on TeamRepository."""
    org_repo = OrganizationRepository(db_session)
    team_repo = TeamRepository(db_session)

    org_in = OrganizationCreate(name="Stark Industries", slug="stark")
    org = await org_repo.create(org_in)

    team_in = TeamCreate(name="Iron Man Lab", organization_id=org.id)
    team = await team_repo.create(team_in)

    teams = await team_repo.get_teams_by_organization(org.id)
    assert len(teams) == 1
    assert teams[0].id == team.id


@pytest.mark.asyncio
async def test_user_repository(db_session: AsyncSession):
    """Test custom queries on UserRepository."""
    org_repo = OrganizationRepository(db_session)
    team_repo = TeamRepository(db_session)
    user_repo = UserRepository(db_session)

    org = await org_repo.create(OrganizationCreate(name="Oscorp", slug="oscorp"))
    team = await team_repo.create(TeamCreate(name="Bio Lab", organization_id=org.id))

    user_in = UserCreate(
        email="norman@oscorp.com",
        full_name="Norman Osborn",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        team_id=team.id
    )
    user = await user_repo.create(user_in)

    # Get by email
    db_user = await user_repo.get_by_email("norman@oscorp.com")
    assert db_user is not None
    assert db_user.id == user.id

    # Get users by team
    users_by_team = await user_repo.get_users_by_team(team.id)
    assert len(users_by_team) == 1
    assert users_by_team[0].id == user.id

    # Get users by organization
    users_by_org = await user_repo.get_users_by_organization(org.id)
    assert len(users_by_org) == 1
    assert users_by_org[0].id == user.id


@pytest.mark.asyncio
async def test_application_repository(db_session: AsyncSession):
    """Test custom queries on ApplicationRepository."""
    org_repo = OrganizationRepository(db_session)
    team_repo = TeamRepository(db_session)
    app_repo = ApplicationRepository(db_session)

    org = await org_repo.create(OrganizationCreate(name="LexCorp", slug="lex"))
    team = await team_repo.create(TeamCreate(name="Defense Division", organization_id=org.id))

    app_in = ApplicationCreate(
        name="Krypton Radar",
        description="Tracks kryptonian activities",
        team_id=team.id
    )
    app = await app_repo.create(app_in)

    # Get apps by team
    apps_by_team = await app_repo.get_applications_by_team(team.id)
    assert len(apps_by_team) == 1
    assert apps_by_team[0].id == app.id

    # Get apps by organization
    apps_by_org = await app_repo.get_applications_by_organization(org.id)
    assert len(apps_by_org) == 1
    assert apps_by_org[0].id == app.id
