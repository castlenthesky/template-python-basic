"""Task model with SQLModel."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, types
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, String, Text

from .base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
  from .user import User


class TaskStatus(str, Enum):
  """Task status enumeration."""

  PENDING = "pending"
  IN_PROGRESS = "in_progress"
  COMPLETED = "completed"
  CANCELLED = "cancelled"


class TaskBase(SQLModel):
  """Base task model with shared fields."""

  title: str = Field(sa_column=Column(String(200), nullable=False), description="Task title")
  description: Optional[str] = Field(
    default=None, sa_column=Column(Text), description="Detailed task description"
  )
  status: TaskStatus = Field(
    default=TaskStatus.PENDING,
    sa_column=Column(String(20), nullable=False),
    description="Current status of the task",
  )
  user_id: UUID = Field(
    sa_column=Column(types.Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False),
    description="UUID of the user who owns this task",
  )


class Task(TaskBase, UUIDMixin, TimestampMixin, table=True):
  """Task table model."""

  __tablename__ = "tasks"  # type: ignore

  completed_at: Optional[datetime] = Field(
    default=None,
    sa_column=Column(DateTime(timezone=True)),
    description="When the task was completed",
  )

  # Relationships
  user: "User" = Relationship(back_populates="tasks")

  def __str__(self) -> str:
    return f"Task(id={self.id}, title='{self.title}', status='{self.status}')"


class TaskCreate(TaskBase):
  """Model for creating a task."""

  pass


class TaskRead(TaskBase):
  """Model for reading a task."""

  id: UUID
  created_at: datetime
  updated_at: datetime
  completed_at: Optional[datetime] = None


class TaskUpdate(SQLModel):
  """Model for updating a task."""

  title: Optional[str] = Field(
    default=None, sa_column=Column(String(200)), description="Updated task title"
  )
  description: Optional[str] = Field(
    default=None, sa_column=Column(Text), description="Updated task description"
  )
  status: Optional[TaskStatus] = Field(default=None, description="Updated task status")
  completed_at: Optional[datetime] = Field(
    default=None,
    sa_column=Column(DateTime(timezone=True)),
    description="When the task was completed",
  )
