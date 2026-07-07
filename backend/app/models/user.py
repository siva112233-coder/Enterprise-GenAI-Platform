import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import UserRole, UserStatus

if TYPE_CHECKING:
    from app.models.team import Team


class User(Base):
    """
    User entity representing a registered platform user.

    A user belongs to a specific team and has defined roles and statuses.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the user"
    )
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
        comment="Email address of the user (must be unique)"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="PBKDF2/bcrypt hashed password (null for SSO/OAuth users)"
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="Display name of the user"
    )
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.VIEWER,
        comment="Role defining permissions of the user"
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus, name="user_status"),
        nullable=False,
        default=UserStatus.ACTIVE,
        comment="Status restricting or permitting access"
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Foreign key linking to the parent team"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the user was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the user was last updated"
    )

    # Relationships
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="users"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
