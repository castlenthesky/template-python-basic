"""User model with SQLModel."""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, String, DateTime
from sqlalchemy import func

if TYPE_CHECKING:
  from .task import Task


class UserBase(SQLModel):
  """Base user model with shared fields."""
  username: str = Field(
    sa_column=Column(String(50), unique=True, nullable=False, index=True),
    description="Unique username for the user"
  )


class User(UserBase, table=True):
  """User table model."""
  __tablename__ = "users"
  
  id: Optional[int] = Field(default=None, primary_key=True)
  created_at: datetime = Field(
    sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    description="When the user was created"
  )
  updated_at: datetime = Field(
    sa_column=Column(
      DateTime(timezone=True), 
      server_default=func.now(),
      onupdate=func.now()
    ),
    description="When the user was last updated"
  )
  
  # Relationships
  tasks: List["Task"] = Relationship(back_populates="user", cascade_delete=True)
  
  def __str__(self) -> str:
    return f"User(id={self.id}, username='{self.username}')"


class UserCreate(UserBase):
  """Model for creating a user."""
  pass


class UserRead(UserBase):
  """Model for reading a user."""
  id: int
  created_at: datetime
  updated_at: datetime


class UserUpdate(SQLModel):
  """Model for updating a user."""
  username: Optional[str] = Field(
    default=None,
    sa_column=Column(String(50)),
    description="Updated username"
  )