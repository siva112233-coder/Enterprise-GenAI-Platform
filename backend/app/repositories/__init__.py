"""
Repositories package — data access layer for the Enterprise GenAI Platform.

PURPOSE
-------
Repositories encapsulate ALL database access logic. Route handlers and services
must NEVER construct SQLAlchemy queries directly — they interact with the
database exclusively through repository methods.

This strict separation provides:
- Testability: repositories are easily mocked in unit tests
- Maintainability: SQL/ORM changes are localised to one layer
- Consistency: query patterns (pagination, filtering, soft-delete) are centralised

CONVENTIONS
-----------
Each repository:
1. Accepts an ``AsyncSession`` in its constructor (injected via ``get_db``).
2. Is scoped to a single ORM model (Single Responsibility Principle).
3. Provides at minimum: ``get_by_id``, ``list``, ``create``, ``update``, ``delete``.
4. Raises domain exceptions (defined in ``app.utils.exceptions``), NOT HTTP exceptions.

STRUCTURE (to be added in future modules)
-----------------------------------------
    repositories/
        base.py          — Generic repository base class with common CRUD operations
        user.py          — UserRepository (future: auth module)
        provider.py      — LLMProviderRepository (future: providers module)
        ...

EXAMPLE (future implementation pattern)
-----------------------------------------
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.repositories.base import BaseRepository
    from app.models.user import User

    class UserRepository(BaseRepository[User]):
        def __init__(self, db: AsyncSession) -> None:
            super().__init__(model=User, db=db)

        async def get_by_email(self, email: str) -> User | None:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
"""
