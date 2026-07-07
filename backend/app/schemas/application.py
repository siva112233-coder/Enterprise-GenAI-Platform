import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApplicationBase(BaseModel):
    """Base fields for an application."""
    name: str = Field(
        ..., max_length=255, description="Name of the client application"
    )
    description: str | None = Field(
        None, max_length=500, description="Optional description of the application"
    )
    is_active: bool = Field(True, description="Flag indicating if the application is active")


class ApplicationCreate(ApplicationBase):
    """Schema for creating a new application."""
    team_id: uuid.UUID = Field(..., description="Owner team ID")


class ApplicationUpdate(BaseModel):
    """Schema for updating an existing application's fields."""
    name: str | None = Field(None, max_length=255, description="Updated application name")
    description: str | None = Field(
        None, max_length=500, description="Updated application description"
    )
    is_active: bool | None = Field(None, description="Updated active status")
    team_id: uuid.UUID | None = Field(None, description="Updated team ID")


class ApplicationResponse(ApplicationBase):
    """Schema representing an application in responses."""
    id: uuid.UUID
    team_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
