"""Integration tests for User repository operations."""

import pytest
from sqlalchemy.orm import Session

from src.database.models.user import UserCreate, UserUpdate
from src.database.operations.user_ops import user_repo


class TestUserRepository:
  """Integration tests for UserRepository."""
  
  def test_create_user_success(self, test_session: Session, sample_user_data):
    """Test creating a new user successfully."""
    # Arrange
    user_create = UserCreate(**sample_user_data)
    
    # Act
    user = user_repo.create_user(test_session, user_create)
    
    # Assert
    assert user.id is not None
    assert user.username == sample_user_data["username"]
    assert user.created_at is not None
    assert user.updated_at is not None
    
  def test_create_user_duplicate_username_fails(self, test_session: Session, sample_user_data):
    """Test that creating a user with duplicate username fails."""
    # Arrange
    user_create = UserCreate(**sample_user_data)
    user_repo.create_user(test_session, user_create)
    
    # Act & Assert
    with pytest.raises(ValueError, match="already exists"):
      user_repo.create_user(test_session, user_create)
  
  def test_get_by_username_existing(self, test_session: Session, sample_user_data):
    """Test getting user by username when user exists."""
    # Arrange
    user_create = UserCreate(**sample_user_data)
    created_user = user_repo.create_user(test_session, user_create)
    
    # Act
    found_user = user_repo.get_by_username(test_session, sample_user_data["username"])
    
    # Assert
    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.username == sample_user_data["username"]
  
  def test_get_by_username_nonexistent(self, test_session: Session):
    """Test getting user by username when user doesn't exist."""
    # Act
    found_user = user_repo.get_by_username(test_session, "nonexistent_user")
    
    # Assert
    assert found_user is None
  
  def test_username_exists_true(self, test_session: Session, sample_user_data):
    """Test username_exists returns True for existing username."""
    # Arrange
    user_create = UserCreate(**sample_user_data)
    user_repo.create_user(test_session, user_create)
    
    # Act
    exists = user_repo.username_exists(test_session, sample_user_data["username"])
    
    # Assert
    assert exists is True
  
  def test_username_exists_false(self, test_session: Session):
    """Test username_exists returns False for non-existing username."""
    # Act
    exists = user_repo.username_exists(test_session, "nonexistent_user")
    
    # Assert
    assert exists is False
  
  def test_get_user_by_id(self, test_session: Session, sample_user_data):
    """Test getting user by ID."""
    # Arrange
    user_create = UserCreate(**sample_user_data)
    created_user = user_repo.create_user(test_session, user_create)
    
    # Act
    found_user = user_repo.get(test_session, created_user.id)
    
    # Assert
    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.username == sample_user_data["username"]
  
  def test_get_multi_users(self, test_session: Session):
    """Test getting multiple users with pagination."""
    # Arrange - create multiple users
    usernames = ["user1", "user2", "user3"]
    created_users = []
    for username in usernames:
      user_create = UserCreate(username=username)
      user = user_repo.create_user(test_session, user_create)
      created_users.append(user)
    
    # Act
    found_users = user_repo.get_multi(test_session, skip=0, limit=10)
    
    # Assert
    assert len(found_users) == 3
    found_usernames = {user.username for user in found_users}
    assert found_usernames == set(usernames)
  
  def test_get_multi_users_with_pagination(self, test_session: Session):
    """Test getting users with pagination limits."""
    # Arrange - create multiple users
    usernames = ["user1", "user2", "user3", "user4", "user5"]
    for username in usernames:
      user_create = UserCreate(username=username)
      user_repo.create_user(test_session, user_create)
    
    # Act
    first_page = user_repo.get_multi(test_session, skip=0, limit=2)
    second_page = user_repo.get_multi(test_session, skip=2, limit=2)
    
    # Assert
    assert len(first_page) == 2
    assert len(second_page) == 2
    # Ensure no overlap
    first_ids = {user.id for user in first_page}
    second_ids = {user.id for user in second_page}
    assert first_ids.isdisjoint(second_ids)
  
  def test_update_user(self, test_session: Session, sample_user_data):
    """Test updating user information."""
    # Arrange
    user_create = UserCreate(**sample_user_data)
    user = user_repo.create_user(test_session, user_create)
    original_updated_at = user.updated_at
    
    # Act
    update_data = UserUpdate(username="updated_username")
    updated_user = user_repo.update(test_session, user, update_data)
    
    # Assert
    assert updated_user.id == user.id
    assert updated_user.username == "updated_username"
    assert updated_user.updated_at >= original_updated_at
  
  def test_delete_user(self, test_session: Session, sample_user_data):
    """Test deleting a user."""
    # Arrange
    user_create = UserCreate(**sample_user_data)
    user = user_repo.create_user(test_session, user_create)
    user_id = user.id
    
    # Act
    deleted_user = user_repo.delete(test_session, user_id)
    
    # Assert
    assert deleted_user is not None
    assert deleted_user.id == user_id
    
    # Verify user is actually deleted
    found_user = user_repo.get(test_session, user_id)
    assert found_user is None
  
  def test_delete_nonexistent_user(self, test_session: Session):
    """Test deleting a user that doesn't exist."""
    # Act
    deleted_user = user_repo.delete(test_session, 999)
    
    # Assert
    assert deleted_user is None
  
  def test_count_users(self, test_session: Session):
    """Test counting total users."""
    # Arrange - create multiple users
    usernames = ["user1", "user2", "user3"]
    for username in usernames:
      user_create = UserCreate(username=username)
      user_repo.create_user(test_session, user_create)
    
    # Act
    count = user_repo.count(test_session)
    
    # Assert
    assert count == 3