"""Shared test database fixtures and utilities for all test types."""

import os
import tempfile
from contextlib import contextmanager
from typing import Generator, Dict, Any, List, Optional
import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlmodel import SQLModel

from src.database.models.user import User, UserCreate
from src.database.models.task import Task, TaskCreate, TaskStatus
from src.database.operations.user_ops import UserRepository
from src.database.operations.task_ops import TaskRepository


class TestDatabaseManager:
  """Manager for test database operations and fixtures."""
  
  def __init__(self, engine: Engine):
    self.engine = engine
    self.session_factory = sessionmaker(
      bind=engine,
      autocommit=False,
      autoflush=False
    )
    self.user_repo = UserRepository()
    self.task_repo = TaskRepository()
  
  @contextmanager
  def get_session(self) -> Generator[Session, None, None]:
    """Get a test database session with automatic rollback."""
    connection = self.engine.connect()
    transaction = connection.begin()
    session = self.session_factory(bind=connection)
    
    try:
      yield session
      session.commit()
    except Exception:
      session.rollback()
      raise
    finally:
      session.close()
      transaction.rollback()
      connection.close()
  
  def create_test_user(self, session: Session, **kwargs) -> User:
    """Create a test user with default or custom values."""
    defaults = {
      "username": "test_user",
    }
    defaults.update(kwargs)
    
    user_create = UserCreate(**defaults)
    return self.user_repo.create_user(session, user_create)
  
  def create_test_task(self, session: Session, user_id: Optional[int] = None, **kwargs) -> Task:
    """Create a test task with default or custom values."""
    if user_id is None:
      # Create a user if none provided
      user = self.create_test_user(session)
      user_id = user.id
    
    defaults = {
      "title": "Test Task",
      "description": "Test task description",
      "status": TaskStatus.PENDING,
      "user_id": user_id,
    }
    defaults.update(kwargs)
    
    task_create = TaskCreate(**defaults)
    return self.task_repo.create(session, task_create)
  
  def create_test_dataset(self, session: Session) -> Dict[str, Any]:
    """Create a comprehensive test dataset with multiple users and tasks."""
    # Create users
    user1 = self.create_test_user(session, username="alice")
    user2 = self.create_test_user(session, username="bob")
    user3 = self.create_test_user(session, username="charlie")
    
    # Create tasks for user1 (alice)
    task1_alice = self.create_test_task(
      session, 
      user_id=user1.id,
      title="Alice's First Task",
      status=TaskStatus.COMPLETED
    )
    task2_alice = self.create_test_task(
      session,
      user_id=user1.id, 
      title="Alice's Second Task",
      status=TaskStatus.IN_PROGRESS
    )
    
    # Create tasks for user2 (bob)
    task1_bob = self.create_test_task(
      session,
      user_id=user2.id,
      title="Bob's Important Task", 
      description="This is very important",
      status=TaskStatus.PENDING
    )
    task2_bob = self.create_test_task(
      session,
      user_id=user2.id,
      title="Bob's Completed Work",
      status=TaskStatus.COMPLETED
    )
    
    # Create task for user3 (charlie)
    task1_charlie = self.create_test_task(
      session,
      user_id=user3.id,
      title="Charlie's Task",
      status=TaskStatus.CANCELLED
    )
    
    return {
      "users": {
        "alice": user1,
        "bob": user2, 
        "charlie": user3,
      },
      "tasks": {
        "alice": [task1_alice, task2_alice],
        "bob": [task1_bob, task2_bob],
        "charlie": [task1_charlie],
      },
      "all_tasks": [task1_alice, task2_alice, task1_bob, task2_bob, task1_charlie],
    }


def create_test_engine(echo: bool = False) -> Engine:
  """Create a test database engine with temporary SQLite file."""
  db_fd, db_path = tempfile.mkstemp(suffix='.db', prefix='test_db_')
  os.close(db_fd)  # Close file descriptor, keep the file
  
  engine = create_engine(
    f"sqlite:///{db_path}",
    echo=echo,
    connect_args={"check_same_thread": False}
  )
  
  # Create all tables
  SQLModel.metadata.create_all(engine)
  
  # Store the path for cleanup
  engine._test_db_path = db_path
  
  return engine


def cleanup_test_engine(engine: Engine) -> None:
  """Clean up test database engine and remove temporary file."""
  if hasattr(engine, '_test_db_path'):
    try:
      engine.dispose()
      os.unlink(engine._test_db_path)
    except OSError:
      pass


# Pytest fixtures for use across all test types

@pytest.fixture(scope="session")
def test_db_engine() -> Generator[Engine, None, None]:
  """Session-scoped test database engine."""
  engine = create_test_engine()
  try:
    yield engine
  finally:
    cleanup_test_engine(engine)


@pytest.fixture(scope="function") 
def test_db_manager(test_db_engine: Engine) -> TestDatabaseManager:
  """Function-scoped test database manager."""
  return TestDatabaseManager(test_db_engine)


@pytest.fixture(scope="function")
def test_session(test_db_manager: TestDatabaseManager) -> Generator[Session, None, None]:
  """Function-scoped test database session with automatic rollback."""
  with test_db_manager.get_session() as session:
    yield session


@pytest.fixture
def test_user(test_session: Session, test_db_manager: TestDatabaseManager) -> User:
  """Fixture providing a single test user."""
  return test_db_manager.create_test_user(test_session)


@pytest.fixture  
def test_task(test_session: Session, test_db_manager: TestDatabaseManager, test_user: User) -> Task:
  """Fixture providing a single test task."""
  return test_db_manager.create_test_task(test_session, user_id=test_user.id)


@pytest.fixture
def test_dataset(test_session: Session, test_db_manager: TestDatabaseManager) -> Dict[str, Any]:
  """Fixture providing a comprehensive test dataset."""
  return test_db_manager.create_test_dataset(test_session)


# Sample data fixtures

@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
  """Sample user data for testing."""
  return {
    "username": "test_user",
  }


@pytest.fixture 
def sample_task_data() -> Dict[str, Any]:
  """Sample task data for testing."""
  return {
    "title": "Test Task",
    "description": "This is a test task",
    "status": TaskStatus.PENDING,
    # user_id will be set in tests
  }


@pytest.fixture
def sample_users_data() -> List[Dict[str, Any]]:
  """Multiple sample users for testing."""
  return [
    {"username": "alice_test"},
    {"username": "bob_test"}, 
    {"username": "charlie_test"},
  ]


@pytest.fixture
def sample_tasks_data() -> List[Dict[str, Any]]:
  """Multiple sample tasks for testing."""
  return [
    {
      "title": "First Task",
      "description": "Description for first task",
      "status": TaskStatus.PENDING,
    },
    {
      "title": "Second Task", 
      "description": "Description for second task",
      "status": TaskStatus.IN_PROGRESS,
    },
    {
      "title": "Third Task",
      "description": "Description for third task", 
      "status": TaskStatus.COMPLETED,
    },
  ]