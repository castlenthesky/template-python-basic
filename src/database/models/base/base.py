"""Base model mixins and common model functionality."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import func, types
from sqlmodel import DateTime, Field, SQLModel


class TimestampMixin(SQLModel):
  """Mixin for models that need created_at and updated_at timestamps."""

  created_at: datetime = Field(
    default=None,
    sa_type=DateTime(timezone=True),
    sa_column_kwargs={
      "server_default": func.now(),
    },
    description="When the record was created",
  )
  updated_at: datetime = Field(
    default=None,
    sa_type=DateTime(timezone=True),
    sa_column_kwargs={
      "server_default": func.now(),
      "onupdate": func.now(),
    },
    description="When the record was last updated",
  )


class UUIDMixin(SQLModel):
  """Mixin for models that use UUID as primary key."""

  id: UUID = Field(
    default_factory=uuid4,
    primary_key=True,
    sa_type=types.Uuid(as_uuid=True),
    description="UUID primary key",
  )


class BaseModel(SQLModel):
  """Base class for all database models with common configuration."""

  class Config:
    """Pydantic configuration for models."""

    from_attributes = True
    validate_assignment = True
    arbitrary_types_allowed = True

  def __repr__(self) -> str:
    """String representation of the model."""
    attrs = []
    for key, value in self.__dict__.items():
      if not key.startswith("_"):
        attrs.append(f"{key}={value!r}")
    return f"{self.__class__.__name__}({', '.join(attrs)})"
