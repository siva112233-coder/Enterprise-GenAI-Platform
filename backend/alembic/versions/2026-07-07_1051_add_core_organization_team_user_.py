"""add core organization team user application tables

Revision ID: 4027212f45e1
Revises: None
Create Date: 2026-07-07 10:51:56.823136+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4027212f45e1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Organization table
    op.create_table(
        "organization",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organization")),
        sa.UniqueConstraint("name", name=op.f("uq_organization_name")),
        sa.UniqueConstraint("slug", name=op.f("uq_organization_slug"))
    )
    op.create_index(op.f("ix_organization_name"), "organization", ["name"], unique=True)
    op.create_index(op.f("ix_organization_slug"), "organization", ["slug"], unique=True)

    # 2. Create Team table
    op.create_table(
        "team",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organization.id"], name=op.f("fk_team_organization_id_organization"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_team"))
    )
    op.create_index(op.f("ix_team_name"), "team", ["name"], unique=False)
    op.create_index(op.f("ix_team_organization_id"), "team", ["organization_id"], unique=False)

    # 3. Create User table
    # Create enum types first in case of PostgreSQL
    role_enum = sa.Enum("ADMIN", "DEVELOPER", "VIEWER", name="user_role")
    role_enum.create(op.get_bind(), checkfirst=True)
    status_enum = sa.Enum("ACTIVE", "INACTIVE", "SUSPENDED", name="user_status")
    status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "user",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.Enum("ADMIN", "DEVELOPER", "VIEWER", name="user_role"), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "INACTIVE", "SUSPENDED", name="user_status"), nullable=False),
        sa.Column("team_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["team.id"], name=op.f("fk_user_team_id_team"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
        sa.UniqueConstraint("email", name=op.f("uq_user_email"))
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_index(op.f("ix_user_team_id"), "user", ["team_id"], unique=False)

    # 4. Create Application table
    op.create_table(
        "application",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("team_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["team.id"], name=op.f("fk_application_team_id_team"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_application"))
    )
    op.create_index(op.f("ix_application_team_id"), "application", ["team_id"], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order of dependencies
    op.drop_index(op.f("ix_application_team_id"), table_name="application")
    op.drop_table("application")

    op.drop_index(op.f("ix_user_team_id"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")

    # Drop enum types
    role_enum = sa.Enum("ADMIN", "DEVELOPER", "VIEWER", name="user_role")
    role_enum.drop(op.get_bind(), checkfirst=True)
    status_enum = sa.Enum("ACTIVE", "INACTIVE", "SUSPENDED", name="user_status")
    status_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_index(op.f("ix_team_organization_id"), table_name="team")
    op.drop_index(op.f("ix_team_name"), table_name="team")
    op.drop_table("team")

    op.drop_index(op.f("ix_organization_slug"), table_name="organization")
    op.drop_index(op.f("ix_organization_name"), table_name="organization")
    op.drop_table("organization")
