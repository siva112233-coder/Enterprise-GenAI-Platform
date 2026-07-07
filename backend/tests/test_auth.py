"""
Integration and unit tests for Module 2B: Authentication & Authorization.
"""

from collections.abc import AsyncGenerator
import uuid
import pytest
from fastapi import APIRouter, Depends, status
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole, UserStatus
from app.models.organization import Organization
from app.models.team import Team
from app.models.user import User
from app.security.dependencies import require_role
from app.security.jwt import create_access_token

# Define a test router specifically for testing role-based access control (RBAC) dependencies
test_router = APIRouter(prefix="/api/v1/test-auth")


@test_router.get("/admin-only", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def admin_only_route() -> dict[str, str]:
    return {"message": "welcome admin"}


@test_router.get(
    "/dev-only",
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.DEVELOPER]))],
)
async def dev_only_route() -> dict[str, str]:
    return {"message": "welcome developer/admin"}


@pytest.fixture(scope="module", autouse=True)
def setup_test_routes(test_app) -> None:
    """Include the test router into the FastAPI test app."""
    test_app.include_router(test_router)


@pytest.fixture(autouse=True)
async def clear_database(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """
    Ensure the test database is clean before and after each test.

    Since client requests run in a separate transaction that gets committed,
    we must explicitly purge records from SQLite to keep tests isolated.
    """
    # Yield control to the test
    yield

    # Clean up all records
    await db_session.execute(delete(User))
    await db_session.execute(delete(Team))
    await db_session.execute(delete(Organization))
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient, db_session: AsyncSession) -> None:
    """Validate that a user can register successfully, resolving/creating org and team."""
    payload = {
        "name": "Bruce Wayne",
        "email": "bruce@waynecorp.com",
        "password": "supersecretpassword123",
        "organization": "Wayne Enterprises",
        "team": "Bat-Family",
        "role": "ADMIN",
    }

    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["email"] == "bruce@waynecorp.com"
    assert data["full_name"] == "Bruce Wayne"
    assert data["role"] == "ADMIN"
    assert data["status"] == "ACTIVE"
    assert "id" in data
    assert "team_id" in data

    # Verify database records exist
    user_stmt = await db_session.execute(
        select(User).where(User.email == "bruce@waynecorp.com")
    )
    user = user_stmt.scalar_one_or_none()
    assert user is not None
    assert user.hashed_password is not None
    assert user.hashed_password != "supersecretpassword123"  # Must be hashed

    # Verify team and organization exist
    team_stmt = await db_session.execute(select(Team).where(Team.id == user.team_id))
    team = team_stmt.scalar_one_or_none()
    assert team is not None
    assert team.name == "Bat-Family"

    org_stmt = await db_session.execute(
        select(Organization).where(Organization.id == team.organization_id)
    )
    org = org_stmt.scalar_one_or_none()
    assert org is not None
    assert org.name == "Wayne Enterprises"
    assert org.slug == "wayne-enterprises"


@pytest.mark.asyncio
async def test_register_user_duplicate_email(client: AsyncClient) -> None:
    """Registration must fail if the email is already registered."""
    payload = {
        "name": "Bruce Wayne",
        "email": "bruce@waynecorp.com",
        "password": "supersecretpassword123",
        "organization": "Wayne Enterprises",
        "team": "Bat-Family",
        "role": "ADMIN",
    }

    # Register first user
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == status.HTTP_201_CREATED

    # Attempt to register second user with same email
    payload["name"] = "Bruce Wayne Shadow"
    res2 = await client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_register_validation_checks(client: AsyncClient) -> None:
    """Validate payload constraints (password length, invalid email format)."""
    # 1. Invalid email
    payload = {
        "name": "Bruce Wayne",
        "email": "not-an-email",
        "password": "validpassword123",
        "organization": "Wayne Enterprises",
        "team": "Bat-Family",
        "role": "ADMIN",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # 2. Password too short
    payload["email"] = "bruce@waynecorp.com"
    payload["password"] = "short"
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    """Validate that a registered user can login and get access/refresh tokens."""
    # Register user
    reg_payload = {
        "name": "Bruce Wayne",
        "email": "bruce@waynecorp.com",
        "password": "supersecretpassword123",
        "organization": "Wayne Enterprises",
        "team": "Bat-Family",
        "role": "ADMIN",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    # Login
    login_payload = {"email": "bruce@waynecorp.com", "password": "supersecretpassword123"}
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800  # Default 30 minutes


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient) -> None:
    """Login must return 401 for incorrect credentials."""
    login_payload = {"email": "nonexistent@waynecorp.com", "password": "somepassword"}
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient) -> None:
    """GET /me must return current user details when authorized."""
    reg_payload = {
        "name": "Bruce Wayne",
        "email": "bruce@waynecorp.com",
        "password": "supersecretpassword123",
        "organization": "Wayne Enterprises",
        "team": "Bat-Family",
        "role": "ADMIN",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {"email": "bruce@waynecorp.com", "password": "supersecretpassword123"}
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    token = login_res.json()["access_token"]

    # Call /me
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["email"] == "bruce@waynecorp.com"
    assert data["full_name"] == "Bruce Wayne"
    assert data["role"] == "ADMIN"
    assert data["team_name"] == "Bat-Family"
    assert data["organization_name"] == "Wayne Enterprises"


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient) -> None:
    """GET /me must return 401 when authorization header is missing or malformed."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {"Authorization": "Bearer invalidtoken123"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_session_success(client: AsyncClient) -> None:
    """Valid refresh tokens must yield a new set of access/refresh tokens."""
    reg_payload = {
        "name": "Bruce Wayne",
        "email": "bruce@waynecorp.com",
        "password": "supersecretpassword123",
        "organization": "Wayne Enterprises",
        "team": "Bat-Family",
        "role": "ADMIN",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {"email": "bruce@waynecorp.com", "password": "supersecretpassword123"}
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    refresh_token = login_res.json()["refresh_token"]

    # Call refresh
    refresh_payload = {"refresh_token": refresh_token}
    response = await client.post("/api/v1/auth/refresh", json=refresh_payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_session_invalid(client: AsyncClient) -> None:
    """Invalid/expired/access tokens passed to refresh must return 401."""
    # 1. Random string
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "randomstring"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # 2. Access token passed as refresh token
    access_token = create_access_token("some-id")
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_role_based_access_control(client: AsyncClient) -> None:
    """Verify require_role dependency correctly restricts and permits users based on role."""
    # Register viewer
    viewer_payload = {
        "name": "Tim Drake",
        "email": "tim@waynecorp.com",
        "password": "password12345",
        "organization": "Wayne Enterprises",
        "team": "Bat-Family",
        "role": "VIEWER",
    }
    await client.post("/api/v1/auth/register", json=viewer_payload)

    # Register developer
    dev_payload = {
        "name": "Barbara Gordon",
        "email": "barbara@waynecorp.com",
        "password": "password12345",
        "organization": "Wayne Enterprises",
        "team": "Bat-Family",
        "role": "DEVELOPER",
    }
    await client.post("/api/v1/auth/register", json=dev_payload)

    # Register admin
    admin_payload = {
        "name": "Bruce Wayne",
        "email": "bruce@waynecorp.com",
        "password": "password12345",
        "organization": "Wayne Enterprises",
        "team": "Bat-Family",
        "role": "ADMIN",
    }
    await client.post("/api/v1/auth/register", json=admin_payload)

    # Get tokens
    async def get_token(email: str) -> str:
        res = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": "password12345"}
        )
        return res.json()["access_token"]

    viewer_token = await get_token("tim@waynecorp.com")
    dev_token = await get_token("barbara@waynecorp.com")
    admin_token = await get_token("bruce@waynecorp.com")

    # TIM (VIEWER) checks
    # Admin only route: expect 403
    res = await client.get(
        "/api/v1/test-auth/admin-only", headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Dev/Admin route: expect 403
    res = await client.get(
        "/api/v1/test-auth/dev-only", headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # BARBARA (DEVELOPER) checks
    # Admin only route: expect 403
    res = await client.get(
        "/api/v1/test-auth/admin-only", headers={"Authorization": f"Bearer {dev_token}"}
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Dev/Admin route: expect 200
    res = await client.get(
        "/api/v1/test-auth/dev-only", headers={"Authorization": f"Bearer {dev_token}"}
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["message"] == "welcome developer/admin"

    # BRUCE (ADMIN) checks
    # Admin only route: expect 200
    res = await client.get(
        "/api/v1/test-auth/admin-only", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["message"] == "welcome admin"

    # Dev/Admin route: expect 200
    res = await client.get(
        "/api/v1/test-auth/dev-only", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == status.HTTP_200_OK
