"""Enhanced base repository class with common CRUD operations."""

import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from sqlalchemy import delete as sql_delete
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from ..interfaces.repository import IRepository

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)

logger = logging.getLogger(__name__)


class BaseRepository(IRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
  """Enhanced base repository with common CRUD operations and error handling."""

  def __init__(self, model: Type[ModelType]):
    """Initialize repository with model class."""
    self.model = model
    self.model_name = model.__name__

  def get(self, session: Session, id: Any) -> Optional[ModelType]:
    """Get a single record by ID."""
    try:
      result = session.get(self.model, id)
      logger.debug(f"Retrieved {self.model_name} with ID: {id}")
      return result
    except Exception as e:
      logger.error(f"Error retrieving {self.model_name} with ID {id}: {e}")
      raise

  def get_multi(
    self,
    session: Session,
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
      results = list(session.execute(statement).scalars().all())
      logger.debug(f"Retrieved {len(results)} {self.model_name} records")
      return results
    except Exception as e:
      logger.error(f"Error retrieving multiple {self.model_name}: {e}")
      raise

  def create(self, session: Session, obj_in: CreateSchemaType) -> ModelType:
    """Create a new record."""
    try:
      obj_data = obj_in.model_dump()
      db_obj = self.model(**obj_data)
      session.add(db_obj)
      session.flush()
      session.refresh(db_obj)
      logger.debug(f"Created {self.model_name} with ID: {getattr(db_obj, 'id', 'N/A')}")
      return db_obj
    except Exception as e:
      logger.error(f"Error creating {self.model_name}: {e}")
      raise

  def update(
    self, session: Session, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
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
      session.flush()
      session.refresh(db_obj)
      logger.debug(f"Updated {self.model_name} with ID: {getattr(db_obj, 'id', 'N/A')}")
      return db_obj
    except Exception as e:
      logger.error(f"Error updating {self.model_name}: {e}")
      raise

  def delete(self, session: Session, id: Any) -> Optional[ModelType]:
    """Delete a record by ID."""
    try:
      obj = session.get(self.model, id)
      if obj:
        session.delete(obj)
        session.flush()
        logger.debug(f"Deleted {self.model_name} with ID: {id}")
      return obj
    except Exception as e:
      logger.error(f"Error deleting {self.model_name} with ID {id}: {e}")
      raise

  def count(self, session: Session, filters: Optional[Dict[str, Any]] = None) -> int:
    """Count records with optional filters."""
    try:
      statement = select(func.count(self.model.id))

      if filters:
        for field, value in filters.items():
          if hasattr(self.model, field):
            statement = statement.where(getattr(self.model, field) == value)

      result = session.execute(statement).scalar()
      logger.debug(f"Counted {result} {self.model_name} records")
      return result or 0
    except Exception as e:
      logger.error(f"Error counting {self.model_name}: {e}")
      raise

  def exists(self, session: Session, id: Any) -> bool:
    """Check if record exists by ID."""
    try:
      statement = select(func.count(self.model.id)).where(self.model.id == id)
      result = session.execute(statement).scalar()
      exists = (result or 0) > 0
      logger.debug(f"{self.model_name} with ID {id} exists: {exists}")
      return exists
    except Exception as e:
      logger.error(f"Error checking existence of {self.model_name} with ID {id}: {e}")
      raise

  def bulk_create(self, session: Session, objs_in: List[CreateSchemaType]) -> List[ModelType]:
    """Bulk create multiple records."""
    try:
      db_objs = []
      for obj_in in objs_in:
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db_objs.append(db_obj)

      session.add_all(db_objs)
      session.flush()

      for db_obj in db_objs:
        session.refresh(db_obj)

      logger.debug(f"Bulk created {len(db_objs)} {self.model_name} records")
      return db_objs
    except Exception as e:
      logger.error(f"Error bulk creating {self.model_name}: {e}")
      raise

  def bulk_update(self, session: Session, updates: List[Dict[str, Any]]) -> List[ModelType]:
    """Bulk update multiple records."""
    try:
      updated_objs = []
      for update_data in updates:
        obj_id = update_data.get("id")
        if not obj_id:
          continue

        db_obj = session.get(self.model, obj_id)
        if not db_obj:
          continue

        for field, value in update_data.items():
          if field != "id" and hasattr(db_obj, field):
            setattr(db_obj, field, value)

        session.add(db_obj)
        updated_objs.append(db_obj)

      session.flush()

      for db_obj in updated_objs:
        session.refresh(db_obj)

      logger.debug(f"Bulk updated {len(updated_objs)} {self.model_name} records")
      return updated_objs
    except Exception as e:
      logger.error(f"Error bulk updating {self.model_name}: {e}")
      raise

  def bulk_delete(self, session: Session, ids: List[Any]) -> int:
    """Bulk delete multiple records by IDs."""
    try:
      statement = sql_delete(self.model).where(self.model.id.in_(ids))
      result = session.execute(statement)
      deleted_count = result.rowcount
      session.flush()
      logger.debug(f"Bulk deleted {deleted_count} {self.model_name} records")
      return deleted_count
    except Exception as e:
      logger.error(f"Error bulk deleting {self.model_name}: {e}")
      raise
