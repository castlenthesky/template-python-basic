"""Task service for business logic operations."""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.database.models.task import Task, TaskCreate, TaskStatus, TaskUpdate
from src.database.repositories.task import TaskRepository

logger = logging.getLogger(__name__)


class TaskService:
  """Task service with business logic methods."""

  def __init__(self):
    """Initialize task service."""
    self._repository = TaskRepository()

  def get_by_user(self, session: Session, user_id: UUID) -> List[Task]:
    """Get all tasks for a specific user."""
    return self._repository.get_by_user(session, user_id)

  def get_by_status(self, session: Session, status: TaskStatus) -> List[Task]:
    """Get tasks by status."""
    return self._repository.get_by_status(session, status)

  def get_completed_tasks(self, session: Session) -> List[Task]:
    """Get completed tasks."""
    return self._repository.get_completed_tasks(session)

  def get_pending_tasks(self, session: Session) -> List[Task]:
    """Get pending tasks."""
    return self._repository.get_pending_tasks(session)

  def get_in_progress_tasks(self, session: Session) -> List[Task]:
    """Get in-progress tasks."""
    return self._repository.get_in_progress_tasks(session)

  def mark_completed(self, session: Session, task_id: UUID) -> Optional[Task]:
    """Mark a task as completed."""
    try:
      task = self._repository.get(session, task_id)
      if task:
        update_data = TaskUpdate(status=TaskStatus.COMPLETED, completed_at=datetime.utcnow())
        updated_task = self._repository.update(session, task, update_data)
        logger.info(f"Marked task {task_id} as completed")
        return updated_task
      logger.warning(f"Task {task_id} not found for completion")
      return None
    except Exception as e:
      logger.error(f"Error marking task {task_id} as completed: {e}")
      raise

  def mark_in_progress(self, session: Session, task_id: UUID) -> Optional[Task]:
    """Mark a task as in progress."""
    try:
      task = self._repository.get(session, task_id)
      if task:
        update_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)
        updated_task = self._repository.update(session, task, update_data)
        logger.info(f"Marked task {task_id} as in progress")
        return updated_task
      logger.warning(f"Task {task_id} not found for status update")
      return None
    except Exception as e:
      logger.error(f"Error marking task {task_id} as in progress: {e}")
      raise

  def mark_cancelled(self, session: Session, task_id: UUID) -> Optional[Task]:
    """Mark a task as cancelled."""
    try:
      task = self._repository.get(session, task_id)
      if task:
        update_data = TaskUpdate(status=TaskStatus.CANCELLED)
        updated_task = self._repository.update(session, task, update_data)
        logger.info(f"Marked task {task_id} as cancelled")
        return updated_task
      logger.warning(f"Task {task_id} not found for cancellation")
      return None
    except Exception as e:
      logger.error(f"Error marking task {task_id} as cancelled: {e}")
      raise

  def search_by_title(self, session: Session, search_term: str) -> List[Task]:
    """Search tasks by title containing the search term."""
    return self._repository.search_by_title(session, search_term)

  def get(self, session: Session, task_id: UUID) -> Optional[Task]:
    """Get task by ID."""
    return self._repository.get(session, task_id)

  def create(self, session: Session, task_create: TaskCreate) -> Task:
    """Create a new task."""
    return self._repository.create(session, task_create)

  def get_multi(self, session: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    """Get multiple tasks."""
    return self._repository.get_multi(session, skip, limit)

  def get_user_tasks_by_status(
    self, session: Session, user_id: UUID, status: TaskStatus
  ) -> List[Task]:
    """Get tasks for a specific user with a specific status."""
    return self._repository.get_user_tasks_by_status(session, user_id, status)
