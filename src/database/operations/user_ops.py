"""User repository for CRUD operations."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from .base import BaseRepository
from ..models.user import User, UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
  """User repository with specialized methods."""
  
  def __init__(self):
    super().__init__(User)
  
  def get_by_username(self, session: Session, username: str) -> Optional[User]:
    """Get user by username."""
    statement = select(User).where(User.username == username)
    return session.execute(statement).scalar_one_or_none()
  
  def username_exists(self, session: Session, username: str) -> bool:
    """Check if username already exists."""
    return self.get_by_username(session, username) is not None
  
  def create_user(self, session: Session, user_create: UserCreate) -> User:
    """Create a new user with validation."""
    if self.username_exists(session, user_create.username):
      raise ValueError(f"Username '{user_create.username}' already exists")
    
    return self.create(session, user_create)
  
  def get_user_with_tasks(self, session: Session, user_id: int) -> Optional[User]:
    """Get user with their tasks loaded."""
    statement = select(User).where(User.id == user_id)
    user = session.execute(statement).scalar_one_or_none()
    if user:
      # Force loading of tasks relationship
      _ = user.tasks
    return user


# Global repository instance
user_repo = UserRepository()