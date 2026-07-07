"""
Models package — SQLAlchemy ORM models for the Enterprise GenAI Platform.

PURPOSE
-------
ORM models represent the database schema as Python classes.
Each model maps directly to a database table and defines:
- Column definitions (types, constraints, defaults)
- Relationships (ForeignKey, relationship())
- Indexes and database-level constraints
- SQLAlchemy events (e.g., before_insert hooks)

CONVENTIONS
-----------
1. ALL models MUST inherit from ``app.db.base.Base``.
2. Table names are automatically derived (snake_case) by the Base class.
3. Every model should include:
   - ``id``: Integer primary key with sequence.
   - ``created_at``: UTC timestamp set at insert time.
   - ``updated_at``: UTC timestamp updated on every write.
4. Use SQLAlchemy 2.0 ``Mapped[]`` + ``mapped_column()`` type-annotated syntax.
5. Avoid business logic in model classes — keep them as data containers.
6. Define indexes at the model level using ``Index()`` in ``__table_args__``.

ALEMBIC INTEGRATION
-------------------
When a new model is added:
1. Import it in ``alembic/env.py`` (or via ``app.models.__init__``) so that
   Alembic's autogenerate can detect it.
2. Run: ``alembic revision --autogenerate -m "add <model_name> table"``
3. Review the generated migration, then: ``alembic upgrade head``

STRUCTURE (to be added in future modules)
-----------------------------------------
    models/
        user.py          — User, UserProfile (auth module)
        provider.py      — LLMProvider, ProviderCredential (providers module)
        usage.py         — UsageRecord, CostEntry (monitoring module)
        agent.py         — AgentDefinition, AgentRun (agents module)
        ...

EXAMPLE (future implementation pattern)
-----------------------------------------
    from datetime import datetime
    from sqlalchemy import String, func
    from sqlalchemy.orm import Mapped, mapped_column
    from app.db.base import Base

    class User(Base):
        id: Mapped[int] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
        hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
        is_active: Mapped[bool] = mapped_column(default=True)
        created_at: Mapped[datetime] = mapped_column(server_default=func.now())
        updated_at: Mapped[datetime] = mapped_column(
            server_default=func.now(), onupdate=func.now()
        )
"""
