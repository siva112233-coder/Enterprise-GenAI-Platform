"""
Authentication service handling user registration, login verification, and token refreshing.
"""

import re
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.core.config import get_settings
from app.models.enums import UserStatus
from app.models.team import Team
from app.models.user import User
from app.repositories.organization import OrganizationRepository
from app.repositories.team import TeamRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    TokenRefreshRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.schemas.organization import OrganizationCreate
from app.schemas.team import TeamCreate
from app.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.security.password import hash_password, verify_password

logger = get_logger(__name__)


def slugify(name: str) -> str:
    """Generate a clean, URL-friendly slug from an organization name."""
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9\s-]", "", name)
    name = re.sub(r"[\s-]+", "-", name)
    return name


class AuthService:
    """Service class for orchestrating all authentication and authorization actions."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the service.

        Args:
            db: The database async session.
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.team_repo = TeamRepository(db)

    async def register_user(self, user_in: UserRegister) -> User:
        """
        Register a new user.

        If the organization or team does not exist, they are created automatically.

        Args:
            user_in: The user registration input data.

        Returns:
            User: The created User ORM instance.

        Raises:
            HTTPException: If email is already registered.
        """
        log = logger.bind(email=user_in.email, organization=user_in.organization, team=user_in.team)
        log.info("Processing user registration request")

        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            log.warning("Registration failed: email already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is already registered.",
            )

        # 1. Resolve or create Organization
        org = await self.org_repo.get_by_name(user_in.organization)
        if not org:
            slug = slugify(user_in.organization)
            collision = await self.org_repo.get_by_slug(slug)
            if collision:
                slug = f"{slug}-{uuid.uuid4().hex[:6]}"

            log.info("Creating new organization", slug=slug)
            org_create = OrganizationCreate(name=user_in.organization, slug=slug)
            org = await self.org_repo.create(org_create)

        # 2. Resolve or create Team
        team_stmt = await self.db.execute(
            select(Team).where(Team.name == user_in.team, Team.organization_id == org.id)
        )
        team = team_stmt.scalar_one_or_none()

        if not team:
            log.info("Creating new team under organization", org_id=org.id)
            team_create = TeamCreate(name=user_in.team, organization_id=org.id)
            team = await self.team_repo.create(team_create)

        # 3. Create User
        hashed_password = hash_password(user_in.password)
        db_user = User(
            email=user_in.email,
            full_name=user_in.name,
            role=user_in.role,
            status=UserStatus.ACTIVE,
            hashed_password=hashed_password,
            team_id=team.id,
        )

        self.db.add(db_user)
        await self.db.flush()

        # Eagerly set relations to prevent greenlet/lazy load exceptions in responses
        db_user.team = team
        db_user.team.organization = org

        log.info("User registered successfully", user_id=str(db_user.id))
        return db_user

    async def login_user(self, login_in: UserLogin) -> TokenResponse:
        """
        Authenticate a user and yield a set of access/refresh tokens.

        Args:
            login_in: Login credentials.

        Returns:
            TokenResponse: Token response fields.

        Raises:
            HTTPException: Invalid credentials or inactive status.
        """
        log = logger.bind(email=login_in.email)
        log.info("Processing user login attempt")

        user = await self.user_repo.get_by_email(login_in.email)
        if not user or not user.hashed_password:
            log.warning("Login failed: invalid email or no password set")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
            )

        if not verify_password(login_in.password, user.hashed_password):
            log.warning("Login failed: password verification failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
            )

        if user.status != UserStatus.ACTIVE:
            log.warning("Login failed: user account status restriction", status=user.status)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is currently inactive or suspended. Please contact support.",
            )

        settings = get_settings()
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        log.info("User authenticated successfully", user_id=str(user.id))

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=refresh_token,
        )

    async def refresh_session(self, refresh_in: TokenRefreshRequest) -> TokenResponse:
        """
        Validate a refresh token and issue new access and refresh tokens.

        Args:
            refresh_in: Payload containing the refresh token.

        Returns:
            TokenResponse: Refreshed token details.

        Raises:
            HTTPException: Invalid token, user not found, or inactive status.
        """
        from jwt.exceptions import PyJWTError

        try:
            payload = decode_token(refresh_in.refresh_token)
            if payload.get("type") != "refresh":
                logger.warning("Session refresh failed: token is not a refresh token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type.",
                )

            sub = payload.get("sub")
            if not sub:
                logger.warning("Session refresh failed: subject payload claim is missing")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Malformed token payload.",
                )

            user_id = uuid.UUID(sub)
        except (PyJWTError, ValueError) as exc:
            logger.warning(
                "Session refresh failed: invalid or expired refresh token signature",
                error=str(exc),
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            ) from exc

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning("Session refresh failed: user no longer exists", user_id=str(user_id))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
            )

        if user.status != UserStatus.ACTIVE:
            logger.warning("Session refresh failed: user account restriction", status=user.status)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is currently inactive or suspended. Please contact support.",
            )

        settings = get_settings()
        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)

        logger.info("Session refreshed successfully", user_id=str(user.id))

        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=new_refresh_token,
        )
