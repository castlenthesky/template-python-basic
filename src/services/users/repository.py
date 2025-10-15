"""User repository for data access operations."""

import logging
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models.public.task import Task
from src.database.models.public.user import User, UserCreate, UserUpdate
from ..shared.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
  """User repository for data access operations."""

  def __init__(self):
    """Initialize user repository."""
    super().__init__(User)

  async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
    """Get user by username."""
    try:
      statement = select(User).where(User.username == username)
      result = await session.execute(statement)
      user = result.scalar_one_or_none()
      logger.debug(f"Retrieved user by username: {username}")
      return user
    except Exception as e:
      logger.error(f"Error retrieving user by username {username}: {e}")
      raise

  async def username_exists(self, session: AsyncSession, username: str) -> bool:
    """Check if username already exists."""
    try:
      result = await self.get_by_username(session, username) is not None
      logger.debug(f"Username '{username}' exists: {result}")
      return result
    except Exception as e:
      logger.error(f"Error checking username existence {username}: {e}")
      raise

  async def get_user_with_tasks(self, session: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user with their tasks loaded using eager loading to prevent N+1 queries."""
    try:
      statement = select(User).options(selectinload(User.tasks)).where(User.id == user_id)
      result = await session.execute(statement)
      user = result.scalar_one_or_none()
      if user:
        logger.debug(f"Retrieved user with tasks: {user.username} ({len(user.tasks)} tasks)")
      return user
    except Exception as e:
      logger.error(f"Error retrieving user with tasks for ID {user_id}: {e}")
      raise

  async def get_users_with_task_counts(
    self, session: AsyncSession, limit: int = 100
  ) -> List[Tuple[User, int]]:
    """Get users with their task counts."""
    try:
      statement = select(User, func.count(Task.id)).outerjoin(Task).group_by(User.id).limit(limit)

      result = await session.execute(statement)
      results = result.all()
      logger.debug(f"Retrieved {len(results)} users with task counts")
      return [(user, count) for user, count in results]
    except Exception as e:
      logger.error(f"Error retrieving users with task counts: {e}")
      raise