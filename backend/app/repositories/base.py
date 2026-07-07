import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class BaseRepository(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    """
    Generic repository base class implementing common CRUD operations.

    All specialized repositories inherit from this class to obtain basic CRUD features
    for a specific SQLAlchemy model.
    """

    def __init__(self, model: type[ModelT], db: AsyncSession) -> None:
        """
        Initialize the repository.

        Args:
            model: The SQLAlchemy model class this repository manages.
            db: The active database AsyncSession instance.
        """
        self.model = model
        self.db = db

    async def get_by_id(self, id: uuid.UUID) -> ModelT | None:
        """
        Retrieve a record by its UUID primary key.

        Args:
            id: The primary key UUID to lookup.

        Returns:
            The mapped model instance or None if not found.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def list(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        """
        Retrieve a list of records with pagination.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.

        Returns:
            A list of model instances.
        """
        result = await self.db.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def create(self, obj_in: CreateSchemaT) -> ModelT:
        """
        Create a new record in the database.

        Args:
            obj_in: The creation schema containing data.

        Returns:
            The created and tracked model instance.
        """
        obj_data = obj_in.model_dump()
        # Filter keys to only those that the model accepts (columns and relationships)
        mapper = self.model.__mapper__
        allowed_keys = set(mapper.columns.keys()) | set(mapper.relationships.keys())
        filtered_data = {k: v for k, v in obj_data.items() if k in allowed_keys}

        db_obj = self.model(**filtered_data)
        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def update(self, db_obj: ModelT, obj_in: UpdateSchemaT | dict[str, Any]) -> ModelT:
        """
        Update an existing database record.

        Args:
            db_obj: The current tracked model instance to update.
            obj_in: The update schema (or dictionary) containing changed fields.

        Returns:
            The updated model instance.
        """
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        # Filter keys to only those that the model accepts
        mapper = self.model.__mapper__
        allowed_keys = set(mapper.columns.keys()) | set(mapper.relationships.keys())

        for field, value in update_data.items():
            if field in allowed_keys:
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def delete(self, id: uuid.UUID) -> ModelT | None:
        """
        Delete a record by its UUID primary key.

        Args:
            id: The primary key UUID of the record to delete.

        Returns:
            The deleted model instance, or None if the record did not exist.
        """
        db_obj = await self.get_by_id(id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.flush()
        return db_obj
