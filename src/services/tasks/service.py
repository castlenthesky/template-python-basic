"""Task service for business logic operations."""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.public.task import Task, TaskCreate, TaskStatus, TaskUpdate
from ..shared.exceptions import NotFoundError
from ..shared.transaction import TransactionalService
from .repository import TaskRepository

logger = logging.getLogger(__name__)


class TaskService(TransactionalService):
  """Task service with business logic methods."""

  def __init__(self, repository: TaskRepository):
    """Initialize task service with repository dependency."""
    self._repository = repository

  async def get_tasks_by_user(self, session: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Task]:
    """Get tasks for a specific user with pagination."""
    # Get all tasks for user first, then apply pagination at repository level if needed
    all_tasks = await self._repository.get_by_user(session, user_id)
    return all_tasks[skip:skip + limit]

  async def get_by_status(self, session: AsyncSession, status: TaskStatus) -> List[Task]:
    """Get tasks by status."""
    return await self._repository.get_by_status(session, status)

  async def get_completed_tasks(self, session: AsyncSession) -> List[Task]:
    """Get completed tasks."""
    return await self.get_by_status(session, TaskStatus.COMPLETED)

  async def get_pending_tasks(self, session: AsyncSession) -> List[Task]:
    """Get pending tasks."""
    return await self.get_by_status(session, TaskStatus.PENDING)

  async def get_in_progress_tasks(self, session: AsyncSession) -> List[Task]:
    """Get in-progress tasks."""
    return await self.get_by_status(session, TaskStatus.IN_PROGRESS)

  async def mark_completed(self, session: AsyncSession, task_id: UUID) -> Optional[Task]:
    """Mark a task as completed."""
    try:
      task = await self._repository.get(session, task_id)
      if not task:
        raise NotFoundError(f"Task {task_id} not found for completion")
      
      update_data = TaskUpdate(status=TaskStatus.COMPLETED, completed_at=datetime.now(timezone.utc))
      updated_task = await self._repository.update(session, task, update_data)
      logger.info(f"Marked task {task_id} as completed")
      return updated_task
    except Exception as e:
      logger.error(f"Error marking task {task_id} as completed: {e}")
      raise

  async def mark_in_progress(self, session: AsyncSession, task_id: UUID) -> Optional[Task]:
    """Mark a task as in progress."""
    try:
      task = await self._repository.get(session, task_id)
      if not task:
        raise NotFoundError(f"Task {task_id} not found for status update")
      
      update_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)
      updated_task = await self._repository.update(session, task, update_data)
      logger.info(f"Marked task {task_id} as in progress")
      return updated_task
    except Exception as e:
      logger.error(f"Error marking task {task_id} as in progress: {e}")
      raise

  async def mark_cancelled(self, session: AsyncSession, task_id: UUID) -> Optional[Task]:
    """Mark a task as cancelled."""
    try:
      task = await self._repository.get(session, task_id)
      if not task:
        raise NotFoundError(f"Task {task_id} not found for cancellation")
      
      update_data = TaskUpdate(status=TaskStatus.CANCELLED)
      updated_task = await self._repository.update(session, task, update_data)
      logger.info(f"Marked task {task_id} as cancelled")
      return updated_task
    except Exception as e:
      logger.error(f"Error marking task {task_id} as cancelled: {e}")
      raise

  async def search_by_title(self, session: AsyncSession, search_term: str) -> List[Task]:
    """Search tasks by title containing the search term."""
    return await self._repository.search_by_title(session, search_term)

  async def get(self, session: AsyncSession, task_id: UUID) -> Optional[Task]:
    """Get task by ID."""
    return await self._repository.get(session, task_id)

  async def create_task(self, session: AsyncSession, task_create: TaskCreate) -> Task:
    """Create a new task."""
    async def _create_task_operation(db_session: AsyncSession) -> Task:
      task = await self._repository.create(db_session, task_create)
      logger.info(f"Created task: {task.title} for user: {task.user_id}")
      return task
    
    return await self.execute_in_transaction(session, _create_task_operation)

  async def get_multi(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Task]:
    """Get multiple tasks."""
    return await self._repository.get_multi(session, skip, limit)

  async def get_user_tasks_by_status(
    self, session: AsyncSession, user_id: UUID, status: TaskStatus
  ) -> List[Task]:
    """Get tasks for a specific user with a specific status."""
    return await self._repository.get_user_tasks_by_status(session, user_id, status)

  async def update_task_status(self, session: AsyncSession, task_id: UUID, status: TaskStatus) -> Optional[Task]:
    """Update task status based on the status type."""
    if status == TaskStatus.COMPLETED:
      return await self.mark_completed(session, task_id)
    elif status == TaskStatus.IN_PROGRESS:
      return await self.mark_in_progress(session, task_id)
    elif status == TaskStatus.CANCELLED:
      return await self.mark_cancelled(session, task_id)
    else:
      # For PENDING or other statuses, use generic update
      task = await self._repository.get(session, task_id)
      if not task:
        raise NotFoundError(f"Task {task_id} not found for status update")
      
      update_data = TaskUpdate(status=status)
      return await self._repository.update(session, task, update_data)

  async def delete(self, session: AsyncSession, task_id: UUID) -> Optional[Task]:
    """Delete task by ID."""
    return await self._repository.delete(session, task_id)

  async def get_overdue_tasks(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Task]:
    """Get overdue tasks."""
    from sqlalchemy import and_, select
    
    try:
      now = datetime.now(timezone.utc)
      statement = select(Task).where(
        and_(
          Task.due_date.isnot(None),
          Task.due_date < now,
          Task.status != TaskStatus.COMPLETED
        )
      ).offset(skip).limit(limit)
      
      result = await session.execute(statement)
      tasks = list(result.scalars().all())
      logger.debug(f"Retrieved {len(tasks)} overdue tasks")
      return tasks
    except Exception as e:
      logger.error(f"Error retrieving overdue tasks: {e}")
      raise

  async def get_tasks_by_priority(self, session: AsyncSession, priority: int, skip: int = 0, limit: int = 100) -> List[Task]:
    """Get tasks by priority level."""
    from sqlalchemy import select
    
    try:
      statement = select(Task).where(Task.priority == priority).offset(skip).limit(limit)
      result = await session.execute(statement)
      tasks = list(result.scalars().all())
      logger.debug(f"Retrieved {len(tasks)} tasks with priority {priority}")
      return tasks
    except Exception as e:
      logger.error(f"Error retrieving tasks with priority {priority}: {e}")
      raise