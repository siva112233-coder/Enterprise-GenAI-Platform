import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrganizationBase(BaseModel):
    """Base fields for an organization."""
    name: str = Field(..., max_length=255, description="Name of the organization")
    slug: str = Field(..., max_length=255, description="URL-friendly slug of the organization")


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an existing organization. All fields are optional."""
    name: str | None = Field(None, max_length=255, description="Updated organization name")
    slug: str | None = Field(None, max_length=255, description="Updated organization slug")


class OrganizationResponse(OrganizationBase):
    """Schema representing an organization in responses."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
