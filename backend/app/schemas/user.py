import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserRole, UserStatus


class UserBase(BaseModel):
    """Base fields for a user."""
    email: EmailStr = Field(..., description="Unique email address of the user")
    full_name: str | None = Field(None, max_length=255, description="Full name of the user")
    role: UserRole = Field(
        UserRole.VIEWER, description="Role of the user defining permission levels"
    )
    status: UserStatus = Field(UserStatus.ACTIVE, description="Account status of the user")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str | None = Field(
        None, min_length=8, max_length=128, description="Raw password for the user"
    )
    team_id: uuid.UUID = Field(..., description="Owner team ID")


class UserUpdate(BaseModel):
    """Schema for updating an existing user's fields. All fields are optional."""
    email: EmailStr | None = Field(None, description="Updated email address")
    full_name: str | None = Field(None, max_length=255, description="Updated full name")
    role: UserRole | None = Field(None, description="Updated user role")
    status: UserStatus | None = Field(None, description="Updated user status")
    password: str | None = Field(
        None, min_length=8, max_length=128, description="Updated raw password"
    )
    team_id: uuid.UUID | None = Field(None, description="Updated team ID")


class UserResponse(UserBase):
    """Schema representing a user in responses. Excludes sensitive data like passwords."""
    id: uuid.UUID
    team_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
