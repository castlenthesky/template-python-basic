"""Base repository class with common CRUD operations."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
  """Base repository with common CRUD operations."""
  
  def __init__(self, model: Type[ModelType]):
    """Initialize repository with model class."""
    self.model = model
  
  def get(self, session: Session, id: Any) -> Optional[ModelType]:
    """Get a single record by ID."""
    return session.get(self.model, id)
  
  def get_multi(
    self, 
    session: Session, 
    skip: int = 0, 
    limit: int = 100
  ) -> List[ModelType]:
    """Get multiple records with pagination."""
    statement = select(self.model).offset(skip).limit(limit)
    return list(session.execute(statement).scalars().all())
  
  def create(self, session: Session, obj_in: CreateSchemaType) -> ModelType:
    """Create a new record."""
    obj_data = obj_in.model_dump()
    db_obj = self.model(**obj_data)
    session.add(db_obj)
    session.flush()
    session.refresh(db_obj)
    return db_obj
  
  def update(
    self, 
    session: Session, 
    db_obj: ModelType, 
    obj_in: Union[UpdateSchemaType, Dict[str, Any]]
  ) -> ModelType:
    """Update an existing record."""
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
    return db_obj
  
  def delete(self, session: Session, id: Any) -> Optional[ModelType]:
    """Delete a record by ID."""
    obj = session.get(self.model, id)
    if obj:
      session.delete(obj)
      session.flush()
    return obj
  
  def count(self, session: Session) -> int:
    """Count total records."""
    statement = select(self.model)
    return len(list(session.execute(statement).scalars().all()))