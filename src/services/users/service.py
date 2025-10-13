"""User service for business logic operations."""

import logging
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.public.user import User, UserCreate
from ..shared.exceptions import DuplicateError, NotFoundError
from .repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
  """User service with business logic methods."""

  def __init__(self):
    """Initialize user service."""
    self._repository = UserRepository()

  async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
    """Get user by username."""
    return await self._repository.get_by_username(session, username)

  async def username_exists(self, session: AsyncSession, username: str) -> bool:
    """Check if username already exists."""
    return await self._repository.username_exists(session, username)

  async def create_user(self, session: AsyncSession, user_create: UserCreate) -> User:
    """Create a new user with validation."""
    try:
      if await self.username_exists(session, user_create.username):
        raise DuplicateError(f"Username '{user_create.username}' already exists")

      user = await self._repository.create(session, user_create)
      logger.info(f"Successfully created user: {user_create.username}")
      return user
    except Exception as e:
      logger.error(f"Error creating user {user_create.username}: {e}")
      raise

  async def get_user_with_tasks(self, session: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user with their tasks loaded."""
    return await self._repository.get_user_with_tasks(session, user_id)

  async def get_users_with_task_counts(
    self, session: AsyncSession, limit: int = 100
  ) -> List[Tuple[User, int]]:
    """Get users with their task counts."""
    return await self._repository.get_users_with_task_counts(session, limit)

  async def get_multi(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Get multiple users."""
    return await self._repository.get_multi(session, skip, limit)

  async def get(self, session: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user by ID."""
    return await self._repository.get(session, user_id)

  async def delete(self, session: AsyncSession, user_id: UUID) -> Optional[User]:
    """Delete user by ID."""
    user = await self._repository.get(session, user_id)
    if not user:
      raise NotFoundError(f"User with ID {user_id} not found")
    return await self._repository.delete(session, user_id)