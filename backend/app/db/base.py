"""
SQLAlchemy declarative base and metadata for the Enterprise GenAI Platform.

All ORM models MUST inherit from ``Base`` to be discovered by:
- SQLAlchemy's mapper registry (relationship resolution)
- Alembic's autogenerate (migration detection)

Naming conventions are enforced at the metadata level to ensure
consistent, predictable constraint names across all databases and
migration scripts (avoids anonymous constraint names like 'uq_1').
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

# ---------------------------------------------------------------------------
# Naming conventions
# ---------------------------------------------------------------------------
# SQLAlchemy / Alembic best practice: explicit constraint names prevent
# issues with databases that require constraint names for DROP/ALTER.
# The placeholders %(table_name)s, %(column_0_name)s, etc. are filled
# in by SQLAlchemy at DDL generation time.
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Shared declarative base for all ORM models.

    Features:
    - Enforced naming conventions for all DDL constraints
    - Automatic ``__tablename__`` derived from the class name
    - Type annotation map placeholder for future custom types

    Usage::

        from app.db.base import Base

        class MyModel(Base):
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(255))
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Derive table name automatically from the class name.

        Converts CamelCase class names to snake_case table names.
        Example: ``UserAccount`` → ``user_account``
        """
        import re

        name = cls.__name__
        # Insert underscore before each uppercase letter (except the first)
        snake = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        return snake
