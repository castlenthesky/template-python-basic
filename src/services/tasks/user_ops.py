"""User service for business logic operations."""

import logging
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from src.database.models.user import User, UserCreate
from src.database.repositories.user import UserRepository

logger = logging.getLogger(__name__)


class UserService:
  """User service with business logic methods."""

  def __init__(self):
    """Initialize user service."""
    self._repository = UserRepository()

  def get_by_username(self, session: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return self._repository.get_by_username(session, username)

  def username_exists(self, session: Session, username: str) -> bool:
    """Check if username already exists."""
    return self._repository.username_exists(session, username)

  def create_user(self, session: Session, user_create: UserCreate) -> User:
    """Create a new user with validation."""
    try:
      if self.username_exists(session, user_create.username):
        raise ValueError(f"Username '{user_create.username}' already exists")

      user = self._repository.create(session, user_create)
      logger.info(f"Successfully created user: {user_create.username}")
      return user
    except Exception as e:
      logger.error(f"Error creating user {user_create.username}: {e}")
      raise

  def get_user_with_tasks(self, session: Session, user_id: UUID) -> Optional[User]:
    """Get user with their tasks loaded."""
    return self._repository.get_user_with_tasks(session, user_id)

  def get_users_with_task_counts(
    self, session: Session, limit: int = 100
  ) -> List[Tuple[User, int]]:
    """Get users with their task counts."""
    return self._repository.get_users_with_task_counts(session, limit)

  def get_multi(self, session: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get multiple users."""
    return self._repository.get_multi(session, skip, limit)

  def get(self, session: Session, user_id: UUID) -> Optional[User]:
    """Get user by ID."""
    return self._repository.get(session, user_id)

  def delete(self, session: Session, user_id: UUID) -> Optional[User]:
    """Delete user by ID."""
    return self._repository.delete(session, user_id)
