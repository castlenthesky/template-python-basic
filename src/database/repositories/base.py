"""Base repository with async CRUD operations."""

import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy import delete as sql_delete
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)

logger = logging.getLogger(__name__)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
  """Base repository with async CRUD operations."""

  def __init__(self, model: Type[ModelType]):
    """Initialize repository with model class."""
    self.model = model
    self.model_name = model.__name__

  async def get(self, session: AsyncSession, id: Any) -> Optional[ModelType]:
    """Get a single record by ID."""
    try:
      result = await session.get(self.model, id)
      logger.debug(f"Retrieved {self.model_name} with ID: {id}")
      return result
    except Exception as e:
      logger.error(f"Error retrieving {self.model_name} with ID {id}: {e}")
      raise

  async def get_multi(
    self,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None,
  ) -> List[ModelType]:
    """Get multiple records with pagination and optional filters."""
    try:
      statement = select(self.model)

      if filters:
        for field, value in filters.items():
          if hasattr(self.model, field):
            statement = statement.where(getattr(self.model, field) == value)

      statement = statement.offset(skip).limit(limit)
      result = await session.execute(statement)
      results = list(result.scalars().all())
      logger.debug(f"Retrieved {len(results)} {self.model_name} records")
      return results
    except Exception as e:
      logger.error(f"Error retrieving multiple {self.model_name}: {e}")
      raise

  async def create(self, session: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
    """Create a new record."""
    try:
      obj_data = obj_in.model_dump()
      db_obj = self.model(**obj_data)
      session.add(db_obj)
      await session.flush()
      await session.refresh(db_obj)
      logger.debug(f"Created {self.model_name} with ID: {getattr(db_obj, 'id', 'N/A')}")
      return db_obj
    except Exception as e:
      logger.error(f"Error creating {self.model_name}: {e}")
      raise

  async def update(
    self, session: AsyncSession, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
  ) -> ModelType:
    """Update an existing record."""
    try:
      if isinstance(obj_in, dict):
        update_data = obj_in
      else:
        update_data = obj_in.model_dump(exclude_unset=True)

      for field, value in update_data.items():
        if hasattr(db_obj, field):
          setattr(db_obj, field, value)

      session.add(db_obj)
      await session.flush()
      await session.refresh(db_obj)
      logger.debug(f"Updated {self.model_name} with ID: {getattr(db_obj, 'id', 'N/A')}")
      return db_obj
    except Exception as e:
      logger.error(f"Error updating {self.model_name}: {e}")
      raise

  async def delete(self, session: AsyncSession, id: Any) -> Optional[ModelType]:
    """Delete a record by ID."""
    try:
      obj = await session.get(self.model, id)
      if obj:
        await session.delete(obj)
        await session.flush()
        logger.debug(f"Deleted {self.model_name} with ID: {id}")
      return obj
    except Exception as e:
      logger.error(f"Error deleting {self.model_name} with ID {id}: {e}")
      raise

  async def count(self, session: AsyncSession, filters: Optional[Dict[str, Any]] = None) -> int:
    """Count records with optional filters."""
    try:
      statement = select(func.count(self.model.id))

      if filters:
        for field, value in filters.items():
          if hasattr(self.model, field):
            statement = statement.where(getattr(self.model, field) == value)

      result = await session.execute(statement)
      count = result.scalar()
      logger.debug(f"Counted {count} {self.model_name} records")
      return count or 0
    except Exception as e:
      logger.error(f"Error counting {self.model_name}: {e}")
      raise

  async def exists(self, session: AsyncSession, id: Any) -> bool:
    """Check if record exists by ID."""
    try:
      statement = select(func.count(self.model.id)).where(self.model.id == id)
      result = await session.execute(statement)
      count = result.scalar()
      exists = (count or 0) > 0
      logger.debug(f"{self.model_name} with ID {id} exists: {exists}")
      return exists
    except Exception as e:
      logger.error(f"Error checking existence of {self.model_name} with ID {id}: {e}")
      raise

  async def bulk_create(self, session: AsyncSession, objs_in: List[CreateSchemaType]) -> List[ModelType]:
    """Bulk create multiple records."""
    try:
      db_objs = []
      for obj_in in objs_in:
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db_objs.append(db_obj)

      session.add_all(db_objs)
      await session.flush()

      for db_obj in db_objs:
        await session.refresh(db_obj)

      logger.debug(f"Bulk created {len(db_objs)} {self.model_name} records")
      return db_objs
    except Exception as e:
      logger.error(f"Error bulk creating {self.model_name}: {e}")
      raise

  async def bulk_update(self, session: AsyncSession, updates: List[Dict[str, Any]]) -> List[ModelType]:
    """Bulk update multiple records."""
    try:
      updated_objs = []
      for update_data in updates:
        obj_id = update_data.get("id")
        if not obj_id:
          continue

        db_obj = await session.get(self.model, obj_id)
        if not db_obj:
          continue

        for field, value in update_data.items():
          if field != "id" and hasattr(db_obj, field):
            setattr(db_obj, field, value)

        session.add(db_obj)
        updated_objs.append(db_obj)

      await session.flush()

      for db_obj in updated_objs:
        await session.refresh(db_obj)

      logger.debug(f"Bulk updated {len(updated_objs)} {self.model_name} records")
      return updated_objs
    except Exception as e:
      logger.error(f"Error bulk updating {self.model_name}: {e}")
      raise

  async def bulk_delete(self, session: AsyncSession, ids: List[Any]) -> int:
    """Bulk delete multiple records by IDs."""
    try:
      statement = sql_delete(self.model).where(self.model.id.in_(ids))
      result = await session.execute(statement)
      deleted_count = result.rowcount
      await session.flush()
      logger.debug(f"Bulk deleted {deleted_count} {self.model_name} records")
      return deleted_count
    except Exception as e:
      logger.error(f"Error bulk deleting {self.model_name}: {e}")
      raise
