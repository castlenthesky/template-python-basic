"""Base model class and metadata configuration."""

from typing import Any
from sqlmodel import SQLModel


class Base(SQLModel):
  """Base class for all database models."""
  
  class Config:
    """Pydantic configuration for models."""
    from_attributes = True
    validate_assignment = True
    arbitrary_types_allowed = True
  
  def __repr__(self) -> str:
    """String representation of the model."""
    attrs = []
    for key, value in self.__dict__.items():
      if not key.startswith('_'):
        attrs.append(f"{key}={value!r}")
    return f"{self.__class__.__name__}({', '.join(attrs)})"