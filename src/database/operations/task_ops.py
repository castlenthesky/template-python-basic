"""Task repository for CRUD operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from .base import BaseRepository
from ..models.task import Task, TaskCreate, TaskUpdate, TaskStatus


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):
  """Task repository with specialized methods."""
  
  def __init__(self):
    super().__init__(Task)
  
  def get_by_user(self, session: Session, user_id: UUID) -> List[Task]:
    """Get all tasks for a specific user."""
    statement = select(Task).where(Task.user_id == user_id)
    return list(session.execute(statement).scalars().all())
  
  def get_by_status(
    self, 
    session: Session, 
    status: TaskStatus, 
    user_id: Optional[UUID] = None
  ) -> List[Task]:
    """Get tasks by status, optionally filtered by user."""
    statement = select(Task).where(Task.status == status)
    if user_id:
      statement = statement.where(Task.user_id == user_id)
    return list(session.execute(statement).scalars().all())
  
  def get_completed_tasks(
    self, 
    session: Session, 
    user_id: Optional[UUID] = None
  ) -> List[Task]:
    """Get completed tasks."""
    return self.get_by_status(session, TaskStatus.COMPLETED, user_id)
  
  def get_pending_tasks(
    self, 
    session: Session, 
    user_id: Optional[UUID] = None
  ) -> List[Task]:
    """Get pending tasks."""
    return self.get_by_status(session, TaskStatus.PENDING, user_id)
  
  def mark_completed(self, session: Session, task_id: UUID) -> Optional[Task]:
    """Mark a task as completed."""
    task = self.get(session, task_id)
    if task:
      update_data = TaskUpdate(
        status=TaskStatus.COMPLETED,
        completed_at=datetime.utcnow()
      )
      return self.update(session, task, update_data)
    return None
  
  def mark_in_progress(self, session: Session, task_id: UUID) -> Optional[Task]:
    """Mark a task as in progress."""
    task = self.get(session, task_id)
    if task:
      update_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)
      return self.update(session, task, update_data)
    return None
  
  def search_by_title(
    self, 
    session: Session, 
    search_term: str, 
    user_id: Optional[UUID] = None
  ) -> List[Task]:
    """Search tasks by title containing the search term."""
    statement = select(Task).where(Task.title.contains(search_term))
    if user_id:
      statement = statement.where(Task.user_id == user_id)
    return list(session.execute(statement).scalars().all())


# Global repository instance
task_repo = TaskRepository()