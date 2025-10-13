"""User model with SQLModel."""

from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Column, Field, Relationship, SQLModel, String

from ..base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
  from .task import Task


class UserBase(SQLModel):
  """Base user model with shared fields."""

  username: str = Field(
    sa_column=Column(String(50), unique=True, nullable=False, index=True),
    description="Unique username for the user",
  )


class User(UserBase, UUIDMixin, TimestampMixin, table=True):
  """User table model."""

  __tablename__ = "users"  # type: ignore

  # Relationships
  tasks: List["Task"] = Relationship(back_populates="user", cascade_delete=True)

  def __str__(self) -> str:
    return f"User(id={self.id}, username='{self.username}')"


class UserCreate(UserBase):
  """Model for creating a user."""

  pass


class UserRead(UserBase, UUIDMixin, TimestampMixin):
  """Model for reading a user."""

  pass


class UserUpdate(SQLModel):
  """Model for updating a user."""

  username: Optional[str] = Field(
    default=None, sa_column=Column(String(50)), description="Updated username"
  )
