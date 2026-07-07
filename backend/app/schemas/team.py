import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TeamBase(BaseModel):
    """Base fields for a team."""
    name: str = Field(..., max_length=255, description="Name of the team")


class TeamCreate(TeamBase):
    """Schema for creating a new team."""
    organization_id: uuid.UUID = Field(..., description="Parent organization ID")


class TeamUpdate(BaseModel):
    """Schema for updating a team's fields."""
    name: str | None = Field(None, max_length=255, description="Updated team name")


class TeamResponse(TeamBase):
    """Schema representing a team in responses."""
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
