"""
Integration tests for Module 2C: Organization Management.
"""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.enums import UserRole, UserStatus
from app.models.organization import Organization
from app.models.team import Team
from app.models.user import User
from app.security.jwt import create_access_token


@pytest.fixture(autouse=True)
async def clear_database(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Ensure the test database is clean before and after each test."""
    yield
    await db_session.execute(delete(Application))
    await db_session.execute(delete(User))
    await db_session.execute(delete(Team))
    await db_session.execute(delete(Organization))
    await db_session.commit()


@pytest.fixture
async def test_data(db_session: AsyncSession) -> dict[str, Any]:
    """Seed base organization, team, and users for testing authorization."""
    # Create Organization
    org = Organization(name="Stark Industries", slug="stark-industries")
    db_session.add(org)
    await db_session.flush()

    # Create Team
    team = Team(name="Iron-Legion", organization_id=org.id)
    db_session.add(team)
    await db_session.flush()

    # Create Users
    # 1. Admin User
    admin = User(
        email="tony@stark.com",
        full_name="Tony Stark",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        team_id=team.id,
    )
    # 2. Developer User
    developer = User(
        email="peter@parker.com",
        full_name="Peter Parker",
        role=UserRole.DEVELOPER,
        status=UserStatus.ACTIVE,
        team_id=team.id,
    )
    # 3. Viewer User
    viewer = User(
        email="happy@stark.com",
        full_name="Happy Hogan",
        role=UserRole.VIEWER,
        status=UserStatus.ACTIVE,
        team_id=team.id,
    )

    db_session.add_all([admin, developer, viewer])
    await db_session.commit()

    return {
        "org": org,
        "team": team,
        "admin": admin,
        "developer": developer,
        "viewer": viewer,
        "tokens": {
            "admin": create_access_token(admin.id),
            "developer": create_access_token(developer.id),
            "viewer": create_access_token(viewer.id),
        },
    }


@pytest.mark.asyncio
async def test_organization_crud(client: AsyncClient, test_data: dict[str, Any]) -> None:
    """Test full CRUD cycle for Organizations with RBAC restrictions."""
    tokens = test_data["tokens"]

    # 1. Read (Viewer has access)
    res = await client.get(
        "/api/v1/organizations", headers={"Authorization": f"Bearer {tokens['viewer']}"}
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["total"] == 1

    # 2. Create (Developer cannot create)
    new_org_payload = {"name": "Oscorp Industries", "slug": "oscorp"}
    res = await client.post(
        "/api/v1/organizations",
        json=new_org_payload,
        headers={"Authorization": f"Bearer {tokens['developer']}"},
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Create (Admin can create)
    res = await client.post(
        "/api/v1/organizations",
        json=new_org_payload,
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_201_CREATED
    org_id = res.json()["id"]

    # 3. Validation checks
    # Duplicate name check
    res = await client.post(
        "/api/v1/organizations",
        json={"name": "Oscorp Industries", "slug": "oscorp-new"},
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST

    # 4. Search and Pagination
    res = await client.get(
        "/api/v1/organizations?search=Oscorp",
        headers={"Authorization": f"Bearer {tokens['viewer']}"},
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["total"] == 1
    assert res.json()["items"][0]["name"] == "Oscorp Industries"

    # 5. Update (Admin can update)
    res = await client.put(
        f"/api/v1/organizations/{org_id}",
        json={"name": "Oscorp Corp"},
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["name"] == "Oscorp Corp"

    # 6. Delete (Admin can delete)
    res = await client.delete(
        f"/api/v1/organizations/{org_id}",
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_team_crud(client: AsyncClient, test_data: dict[str, Any]) -> None:
    """Test full CRUD cycle for Teams."""
    tokens = test_data["tokens"]
    org_id = test_data["org"].id

    # 1. List
    res = await client.get(
        f"/api/v1/teams?organization_id={org_id}",
        headers={"Authorization": f"Bearer {tokens['viewer']}"},
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["total"] == 1

    # 2. Create (Admin only)
    res = await client.post(
        "/api/v1/teams",
        json={"name": "Avengers", "organization_id": str(org_id)},
        headers={"Authorization": f"Bearer {tokens['developer']}"},
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    res = await client.post(
        "/api/v1/teams",
        json={"name": "Avengers", "organization_id": str(org_id)},
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_201_CREATED
    team_id = res.json()["id"]

    # 3. Duplicate checks per org
    res = await client.post(
        "/api/v1/teams",
        json={"name": "Avengers", "organization_id": str(org_id)},
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST

    # 4. Search and filter
    res = await client.get(
        "/api/v1/teams?search=Aven",
        headers={"Authorization": f"Bearer {tokens['viewer']}"},
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["total"] == 1

    # 5. Update (Admin only)
    res = await client.put(
        f"/api/v1/teams/{team_id}",
        json={"name": "Avengers-New"},
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_200_OK

    # 6. Delete
    res = await client.delete(
        f"/api/v1/teams/{team_id}",
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_user_management(client: AsyncClient, test_data: dict[str, Any]) -> None:
    """Test full user CRUD, validation, and self-update limitations."""
    tokens = test_data["tokens"]
    team_id = test_data["team"].id
    developer = test_data["developer"]
    viewer = test_data["viewer"]

    # 1. List and Filter
    res = await client.get(
        "/api/v1/users?role=DEVELOPER",
        headers={"Authorization": f"Bearer {tokens['viewer']}"},
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["total"] == 1
    assert res.json()["items"][0]["email"] == "peter@parker.com"

    # 2. Create (Admin only)
    res = await client.post(
        "/api/v1/users",
        json={
            "email": "natasha@stark.com",
            "full_name": "Natasha Romanoff",
            "password": "redroompassword",
            "role": "DEVELOPER",
            "team_id": str(team_id),
        },
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_201_CREATED
    new_user_id = res.json()["id"]

    # 3. Developer Self-Update Success (Name, Email, password)
    res = await client.put(
        f"/api/v1/users/{developer.id}",
        json={"full_name": "Peter B. Parker", "email": "peter.parker@stark.com"},
        headers={"Authorization": f"Bearer {tokens['developer']}"},
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["full_name"] == "Peter B. Parker"
    assert res.json()["email"] == "peter.parker@stark.com"

    # 4. Developer Self-Update Blocked fields (Role elevation, Team change)
    res = await client.put(
        f"/api/v1/users/{developer.id}",
        json={"role": "ADMIN"},
        headers={"Authorization": f"Bearer {tokens['developer']}"},
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # 5. Developer updating other user (Blocked)
    res = await client.put(
        f"/api/v1/users/{viewer.id}",
        json={"full_name": "Happy"},
        headers={"Authorization": f"Bearer {tokens['developer']}"},
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # 6. Admin updating fields on any user (Allowed)
    res = await client.put(
        f"/api/v1/users/{developer.id}",
        json={"role": "ADMIN", "status": "SUSPENDED"},
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["role"] == "ADMIN"
    assert res.json()["status"] == "SUSPENDED"

    # 7. Delete User (Admin only)
    res = await client.delete(
        f"/api/v1/users/{new_user_id}",
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_application_crud(client: AsyncClient, test_data: dict[str, Any]) -> None:
    """Test full application CRUD, validation, and filters."""
    tokens = test_data["tokens"]
    team_id = test_data["team"].id

    # 1. Create (Admin only)
    app_payload = {
        "name": "Mark-85",
        "description": "Armor control system",
        "is_active": True,
        "team_id": str(team_id),
    }
    res = await client.post(
        "/api/v1/applications",
        json=app_payload,
        headers={"Authorization": f"Bearer {tokens['developer']}"},
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    res = await client.post(
        "/api/v1/applications",
        json=app_payload,
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_201_CREATED
    app_id = res.json()["id"]

    # 2. Unique name within team check
    res = await client.post(
        "/api/v1/applications",
        json=app_payload,
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST

    # 3. List and Filters
    res = await client.get(
        f"/api/v1/applications?team_id={team_id}&is_active=true",
        headers={"Authorization": f"Bearer {tokens['viewer']}"},
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["total"] == 1
    assert res.json()["items"][0]["name"] == "Mark-85"

    # 4. Update
    res = await client.put(
        f"/api/v1/applications/{app_id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["is_active"] is False

    # 5. Delete
    res = await client.delete(
        f"/api/v1/applications/{app_id}",
        headers={"Authorization": f"Bearer {tokens['admin']}"},
    )
    assert res.status_code == status.HTTP_200_OK
