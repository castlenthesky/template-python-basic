"""Task repository for async data access operations."""

import logging
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.task import Task, TaskCreate, TaskStatus, TaskUpdate
from .base import BaseRepository

logger = logging.getLogger(__name__)


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):
  """Task repository with specialized async data access methods."""

  def __init__(self):
    """Initialize task repository."""
    super().__init__(Task)

  async def get_by_user(self, session: AsyncSession, user_id: UUID) -> List[Task]:
    """Get all tasks for a specific user."""
    try:
      statement = select(Task).where(Task.user_id == user_id)
      result = await session.execute(statement)
      results = list(result.scalars().all())
      logger.debug(f"Retrieved {len(results)} tasks for user: {user_id}")
      return results
    except Exception as e:
      logger.error(f"Error retrieving tasks for user {user_id}: {e}")
      raise

  async def get_by_status(self, session: AsyncSession, status: TaskStatus) -> List[Task]:
    """Get all tasks with a specific status."""
    try:
      statement = select(Task).where(Task.status == status)
      result = await session.execute(statement)
      results = list(result.scalars().all())
      logger.debug(f"Retrieved {len(results)} tasks with status: {status}")
      return results
    except Exception as e:
      logger.error(f"Error retrieving tasks with status {status}: {e}")
      raise

  async def get_completed_tasks(self, session: AsyncSession) -> List[Task]:
    """Get all completed tasks."""
    return await self.get_by_status(session, TaskStatus.COMPLETED)

  async def get_pending_tasks(self, session: AsyncSession) -> List[Task]:
    """Get all pending tasks."""
    return await self.get_by_status(session, TaskStatus.PENDING)

  async def get_in_progress_tasks(self, session: AsyncSession) -> List[Task]:
    """Get all in-progress tasks."""
    return await self.get_by_status(session, TaskStatus.IN_PROGRESS)

  async def search_by_title(self, session: AsyncSession, title_search: str) -> List[Task]:
    """Search tasks by title (case-insensitive partial match)."""
    try:
      statement = select(Task).where(Task.title.ilike(f"%{title_search}%"))
      result = await session.execute(statement)
      results = list(result.scalars().all())
      logger.debug(f"Found {len(results)} tasks matching title search: {title_search}")
      return results
    except Exception as e:
      logger.error(f"Error searching tasks by title '{title_search}': {e}")
      raise

  async def get_user_tasks_by_status(
    self, session: AsyncSession, user_id: UUID, status: TaskStatus
  ) -> List[Task]:
    """Get tasks for a specific user with a specific status."""
    try:
      statement = select(Task).where((Task.user_id == user_id) & (Task.status == status))
      result = await session.execute(statement)
      results = list(result.scalars().all())
      logger.debug(f"Retrieved {len(results)} {status} tasks for user: {user_id}")
      return results
    except Exception as e:
      logger.error(f"Error retrieving {status} tasks for user {user_id}: {e}")
      raise
