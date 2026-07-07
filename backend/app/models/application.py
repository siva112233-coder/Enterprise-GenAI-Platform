import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.team import Team


class Application(Base):
    """
    Application entity representing a client app registered to consume the GenAI Gateway.

    Each application belongs to a specific Team and is used to track API usage and credentials.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the application"
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Name of the application"
    )
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        comment="Optional description of the application's purpose"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Flag indicating whether this application can consume the gateway"
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Foreign key linking to the owner team"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the application was registered"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the application was last updated"
    )

    # Relationships
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="applications"
    )

    def __repr__(self) -> str:
        return f"<Application id={self.id} name={self.name} team_id={self.team_id}>"
