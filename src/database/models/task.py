"""Task model with SQLModel."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, Column, String, DateTime, Text
from sqlalchemy import func, ForeignKey

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
  title: str = Field(
    sa_column=Column(String(200), nullable=False),
    description="Task title"
  )
  description: Optional[str] = Field(
    default=None,
    sa_column=Column(Text),
    description="Detailed task description"
  )
  status: TaskStatus = Field(
    default=TaskStatus.PENDING,
    description="Current status of the task"
  )
  user_id: int = Field(
    foreign_key="users.id",
    description="ID of the user who owns this task"
  )


class Task(TaskBase, table=True):
  """Task table model."""
  __tablename__ = "tasks"
  
  id: Optional[int] = Field(default=None, primary_key=True)
  created_at: datetime = Field(
    sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    description="When the task was created"
  )
  updated_at: datetime = Field(
    sa_column=Column(
      DateTime(timezone=True),
      server_default=func.now(), 
      onupdate=func.now()
    ),
    description="When the task was last updated"
  )
  completed_at: Optional[datetime] = Field(
    default=None,
    sa_column=Column(DateTime(timezone=True)),
    description="When the task was completed"
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
  id: int
  created_at: datetime
  updated_at: datetime
  completed_at: Optional[datetime] = None


class TaskUpdate(SQLModel):
  """Model for updating a task."""
  title: Optional[str] = Field(
    default=None,
    sa_column=Column(String(200)),
    description="Updated task title"
  )
  description: Optional[str] = Field(
    default=None,
    sa_column=Column(Text),
    description="Updated task description"
  )
  status: Optional[TaskStatus] = Field(
    default=None,
    description="Updated task status"
  )
  completed_at: Optional[datetime] = Field(
    default=None,
    sa_column=Column(DateTime(timezone=True)),
    description="When the task was completed"
  )