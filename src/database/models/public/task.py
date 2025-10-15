"""Task model with SQLModel."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, types
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, String, Text

from ..base import TimestampMixin, UUIDMixin
from .base import ExampleBase

if TYPE_CHECKING:
  from .user import User


class TaskStatus(str, Enum):
  """Task status enumeration."""

  PENDING = "pending"
  IN_PROGRESS = "in_progress"
  COMPLETED = "completed"
  CANCELLED = "cancelled"


class TaskBase(ExampleBase):
  """Base task model with shared fields."""

  title: str = Field(sa_column=Column(String(200), nullable=False), description="Task title")
  description: Optional[str] = Field(
    default=None, sa_column=Column(Text), description="Detailed task description"
  )
  priority: Optional[int] = Field(
    default=None,
    sa_column=Column(Integer, index=True),
    description="Task priority, 1 is the highest, 5 is the lowest",
  )
  due_date: Optional[datetime] = Field(
    default=None, sa_column=Column(DateTime(timezone=True), index=True), description="When the task is due"
  )
  status: TaskStatus = Field(
    default=TaskStatus.PENDING,
    sa_column=Column(String(20), nullable=False, index=True),
    description="Current status of the task",
  )
  user_id: UUID = Field(
    sa_column=Column(types.Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True),
    description="UUID of the user who owns this task",
  )


class Task(TaskBase, UUIDMixin, TimestampMixin, table=True):
  """Task table model."""

  __tablename__: ClassVar[str] = "tasks"

  completed_at: Optional[datetime] = Field(
    default=None,
    sa_column=Column(DateTime(timezone=True)),
    description="When the task was completed",
  )

  # Relationships
  user: "User" = Relationship(back_populates="tasks")
  
  # Composite indexes for optimized queries
  __table_args__ = (
    # Index for user + status queries (most common pattern)
    Index("idx_task_user_status", "user_id", "status"),
    # Index for user + priority queries
    Index("idx_task_user_priority", "user_id", "priority"),
    # Index for status + due_date queries (overdue tasks)
    Index("idx_task_status_due_date", "status", "due_date"),
    # Index for user + due_date queries (user's upcoming tasks)
    Index("idx_task_user_due_date", "user_id", "due_date"),
    # Index for created_at for time-based queries
    Index("idx_task_created_at", "created_at"),
  )

  def __str__(self) -> str:
    return f"Task(id={self.id}, title='{self.title}', status='{self.status}')"


class TaskCreate(TaskBase):
  """Model for creating a task."""

  pass


class TaskRead(TaskBase, UUIDMixin, TimestampMixin):
  """Model for reading a task."""

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
