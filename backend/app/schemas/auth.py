"""
Pydantic schemas for request validation and response serialization in authentication.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserRole, UserStatus


class UserRegister(BaseModel):
    """Schema for user registration request."""

    name: str = Field(..., min_length=1, max_length=255, description="Full name of the user")
    email: EmailStr = Field(..., description="Unique email address of the user")
    password: str = Field(
        ..., min_length=8, max_length=128, description="Plaintext password for the user"
    )
    organization: str = Field(
        ..., min_length=1, max_length=255, description="Name of the organization"
    )
    team: str = Field(..., min_length=1, max_length=255, description="Name of the team")
    role: UserRole = Field(UserRole.VIEWER, description="Requested role level for authorization")


class UserLogin(BaseModel):
    """Schema for user login request."""

    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., description="Plaintext password for verification")


class TokenResponse(BaseModel):
    """Response schema containing JWT access and refresh tokens."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token authentication scheme (bearer)")
    expires_in: int = Field(..., description="Access token lifetime in seconds")
    refresh_token: str = Field(..., description="JWT refresh token")


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="JWT refresh token")


class UserMeResponse(BaseModel):
    """Detailed response schema representing the currently authenticated user's profile."""

    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    role: UserRole
    status: UserStatus
    team_id: uuid.UUID
    team_name: str
    organization_id: uuid.UUID
    organization_name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
