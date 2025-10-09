"""Integration tests for database session management."""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database import session_scope, get_session, SessionLocal
from src.database.models.user import UserCreate, User
from src.database.models.task import TaskCreate, TaskStatus
from src.database.operations.user_ops import user_repo
from src.database.operations.task_ops import task_repo


class TestSessionManagement:
  """Integration tests for database session management patterns."""
  
  def test_session_scope_context_manager_success(self, test_db_engine):
    """Test session_scope context manager with successful operations."""
    # Arrange
    user_data = UserCreate(username="context_test_user")
    
    # Act
    with session_scope() as session:
      user = user_repo.create_user(session, user_data)
      created_user_id = user.id
    
    # Assert - Verify data was committed
    with session_scope() as session:
      found_user = user_repo.get(session, created_user_id)
      assert found_user is not None
      assert found_user.username == "context_test_user"
  
  def test_session_scope_context_manager_rollback_on_exception(self, test_db_engine):
    """Test session_scope context manager rolls back on exception."""
    # Arrange
    user_data = UserCreate(username="rollback_test_user")
    
    # Act & Assert
    with pytest.raises(ValueError, match="Test exception"):
      with session_scope() as session:
        user_repo.create_user(session, user_data)
        # Force an exception to trigger rollback
        raise ValueError("Test exception")
    
    # Verify rollback - user should not exist
    with session_scope() as session:
      found_user = user_repo.get_by_username(session, "rollback_test_user")
      assert found_user is None
  
  def test_session_scope_context_manager_rollback_on_integrity_error(self, test_db_engine):
    """Test session_scope rolls back on database integrity errors."""
    # Arrange - create user first
    username = "duplicate_test_user"
    user_data = UserCreate(username=username)
    
    with session_scope() as session:
      user_repo.create_user(session, user_data)
    
    # Act & Assert - try to create duplicate user
    with pytest.raises(ValueError, match="already exists"):
      with session_scope() as session:
        # This should raise an exception due to duplicate username
        user_repo.create_user(session, user_data)
    
    # Verify only one user exists
    with session_scope() as session:
      users = user_repo.get_multi(session, limit=100)
      duplicate_users = [u for u in users if u.username == username]
      assert len(duplicate_users) == 1
  
  def test_get_session_dependency_injection_pattern(self, test_db_engine):
    """Test get_session function for dependency injection pattern."""
    # Arrange
    def simulate_fastapi_endpoint():
      """Simulate a FastAPI endpoint using dependency injection."""
      session_gen = get_session()
      session = next(session_gen)
      
      try:
        # Create user
        user_data = UserCreate(username="dependency_test_user")
        user = user_repo.create_user(session, user_data)
        return user.id
      except Exception:
        session.rollback()
        raise
      finally:
        session.close()
    
    # Act
    created_user_id = simulate_fastapi_endpoint()
    
    # Assert - Verify user was created
    with session_scope() as session:
      found_user = user_repo.get(session, created_user_id)
      assert found_user is not None
      assert found_user.username == "dependency_test_user"
  
  def test_get_session_handles_exceptions(self, test_db_engine):
    """Test get_session properly handles exceptions."""
    # Arrange
    def simulate_failing_endpoint():
      """Simulate a FastAPI endpoint that fails."""
      session_gen = get_session()
      session = next(session_gen)
      
      try:
        # Create user
        user_data = UserCreate(username="failing_test_user")
        user_repo.create_user(session, user_data)
        
        # Force an exception
        raise RuntimeError("Simulated endpoint failure")
      except Exception:
        session.rollback()
        raise
      finally:
        session.close()
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Simulated endpoint failure"):
      simulate_failing_endpoint()
    
    # Verify user was not created due to rollback
    with session_scope() as session:
      found_user = user_repo.get_by_username(session, "failing_test_user")
      assert found_user is None
  
  def test_multiple_concurrent_sessions(self, test_db_engine):
    """Test multiple concurrent sessions work independently."""
    # Act - Create users in separate sessions
    user_ids = []
    for i in range(3):
      with session_scope() as session:
        user_data = UserCreate(username=f"concurrent_user_{i}")
        user = user_repo.create_user(session, user_data)
        user_ids.append(user.id)
    
    # Assert - All users should be created
    with session_scope() as session:
      for user_id in user_ids:
        found_user = user_repo.get(session, user_id)
        assert found_user is not None
      
      # Verify total count
      all_users = user_repo.get_multi(session, limit=100)
      concurrent_users = [u for u in all_users if u.username.startswith("concurrent_user_")]
      assert len(concurrent_users) == 3
  
  def test_session_isolation(self, test_db_engine):
    """Test that sessions are properly isolated."""
    # Arrange
    username = "isolation_test_user"
    user_data = UserCreate(username=username)
    
    # Act - Create user in one session, but don't commit
    session1 = SessionLocal()
    try:
      user = user_repo.create_user(session1, user_data)
      created_user_id = user.id
      
      # Check from another session - should not see uncommitted data
      with session_scope() as session2:
        found_user = user_repo.get(session2, created_user_id)
        assert found_user is None  # Shouldn't see uncommitted data
      
      # Commit first session
      session1.commit()
      
      # Now check from another session - should see committed data
      with session_scope() as session2:
        found_user = user_repo.get(session2, created_user_id)
        assert found_user is not None
        assert found_user.username == username
        
    finally:
      session1.close()
  
  def test_transaction_boundaries(self, test_db_engine):
    """Test proper transaction boundaries and commits."""
    # Arrange
    users_data = [
      UserCreate(username="transaction_user_1"),
      UserCreate(username="transaction_user_2"),
      UserCreate(username="transaction_user_3"),
    ]
    
    # Act - Create multiple users in one transaction
    with session_scope() as session:
      created_users = []
      for user_data in users_data:
        user = user_repo.create_user(session, user_data)
        created_users.append(user)
      # All commits happen at end of context manager
    
    # Assert - All users should be committed together
    with session_scope() as session:
      for user in created_users:
        found_user = user_repo.get(session, user.id)
        assert found_user is not None
  
  def test_nested_operations_in_session(self, test_db_engine):
    """Test multiple related operations in single session."""
    # Act
    with session_scope() as session:
      # Create user
      user_data = UserCreate(username="nested_ops_user")
      user = user_repo.create_user(session, user_data)
      
      # Create multiple tasks for the user
      task_titles = ["Task 1", "Task 2", "Task 3"]
      created_tasks = []
      
      for title in task_titles:
        task_data = TaskCreate(
          title=title,
          description=f"Description for {title}",
          user_id=user.id
        )
        task = task_repo.create(session, task_data)
        created_tasks.append(task)
      
      # Update one task status
      task_repo.mark_completed(session, created_tasks[0].id)
    
    # Assert - All operations should be committed
    with session_scope() as session:
      # Verify user exists
      found_user = user_repo.get_by_username(session, "nested_ops_user")
      assert found_user is not None
      
      # Verify all tasks exist
      user_tasks = task_repo.get_by_user(session, found_user.id)
      assert len(user_tasks) == 3
      
      # Verify one task is completed
      completed_tasks = [t for t in user_tasks if t.status == TaskStatus.COMPLETED]
      assert len(completed_tasks) == 1
      
      # Verify relationship works
      assert len(found_user.tasks) == 3
  
  def test_session_cleanup_on_error(self, test_db_engine):
    """Test proper session cleanup even when errors occur."""
    # This test verifies that sessions are properly closed and don't leak
    
    session_created = False
    
    def create_failing_operation():
      nonlocal session_created
      with session_scope() as session:
        session_created = True
        # Create a user
        user_data = UserCreate(username="cleanup_test_user")
        user_repo.create_user(session, user_data)
        # Force an error after creating user
        raise RuntimeError("Intentional test error")
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Intentional test error"):
      create_failing_operation()
    
    assert session_created  # Verify session was created
    
    # Verify cleanup worked - user should not exist due to rollback
    with session_scope() as session:
      found_user = user_repo.get_by_username(session, "cleanup_test_user")
      assert found_user is None