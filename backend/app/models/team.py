import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.organization import Organization
    from app.models.user import User


class Team(Base):
    """
    Team entity representing a business unit or working group within an Organization.

    A team manages multiple users and client applications.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the team"
    )
    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
        comment="Display name of the team"
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organization.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Foreign key linking to the parent organization"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the team was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the team was last updated"
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="teams"
    )
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="team",
        cascade="all, delete-orphan"
    )
    applications: Mapped[list["Application"]] = relationship(
        "Application",
        back_populates="team",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Team id={self.id} name={self.name} organization_id={self.organization_id}>"
