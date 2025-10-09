"""Integration tests for Task repository operations."""

from datetime import datetime
import pytest
from sqlalchemy.orm import Session

from src.database.models.task import Task, TaskCreate, TaskUpdate, TaskStatus
from src.database.models.user import User, UserCreate
from src.database.operations.task_ops import task_repo
from src.database.operations.user_ops import user_repo


class TestTaskRepository:
  """Integration tests for TaskRepository."""
  
  def test_create_task_success(self, test_session: Session, test_user: User):
    """Test creating a new task successfully."""
    # Arrange
    task_data = {
      "title": "New Task",
      "description": "Task description", 
      "user_id": test_user.id,
    }
    task_create = TaskCreate(**task_data)
    
    # Act
    task = task_repo.create(test_session, task_create)
    
    # Assert
    assert task.id is not None
    assert task.title == task_data["title"]
    assert task.description == task_data["description"]
    assert task.user_id == test_user.id
    assert task.status == TaskStatus.PENDING  # Default status
    assert task.created_at is not None
    assert task.updated_at is not None
    assert task.completed_at is None
  
  def test_get_task_by_id(self, test_session: Session, test_task: Task):
    """Test getting task by ID."""
    # Act
    found_task = task_repo.get(test_session, test_task.id)
    
    # Assert
    assert found_task is not None
    assert found_task.id == test_task.id
    assert found_task.title == test_task.title
  
  def test_get_nonexistent_task(self, test_session: Session):
    """Test getting task that doesn't exist."""
    # Act
    found_task = task_repo.get(test_session, 999)
    
    # Assert
    assert found_task is None
  
  def test_get_tasks_by_user(self, test_session: Session, test_dataset):
    """Test getting all tasks for a specific user."""
    # Arrange
    alice = test_dataset["users"]["alice"]
    expected_alice_tasks = test_dataset["tasks"]["alice"]
    
    # Act
    alice_tasks = task_repo.get_by_user(test_session, alice.id)
    
    # Assert
    assert len(alice_tasks) == len(expected_alice_tasks)
    task_ids = {task.id for task in alice_tasks}
    expected_ids = {task.id for task in expected_alice_tasks}
    assert task_ids == expected_ids
  
  def test_get_tasks_by_status(self, test_session: Session, test_dataset):
    """Test getting tasks filtered by status."""
    # Act
    completed_tasks = task_repo.get_by_status(test_session, TaskStatus.COMPLETED)
    pending_tasks = task_repo.get_by_status(test_session, TaskStatus.PENDING)
    in_progress_tasks = task_repo.get_by_status(test_session, TaskStatus.IN_PROGRESS)
    
    # Assert
    assert len(completed_tasks) == 2  # Alice and Bob each have 1 completed
    assert len(pending_tasks) == 1   # Bob has 1 pending
    assert len(in_progress_tasks) == 1  # Alice has 1 in progress
    
    # Verify all completed tasks have correct status
    for task in completed_tasks:
      assert task.status == TaskStatus.COMPLETED
  
  def test_get_tasks_by_status_and_user(self, test_session: Session, test_dataset):
    """Test getting tasks filtered by status and user."""
    # Arrange
    alice = test_dataset["users"]["alice"]
    bob = test_dataset["users"]["bob"]
    
    # Act
    alice_completed = task_repo.get_by_status(test_session, TaskStatus.COMPLETED, alice.id)
    bob_completed = task_repo.get_by_status(test_session, TaskStatus.COMPLETED, bob.id)
    
    # Assert
    assert len(alice_completed) == 1
    assert len(bob_completed) == 1
    assert alice_completed[0].user_id == alice.id
    assert bob_completed[0].user_id == bob.id
  
  def test_get_completed_tasks(self, test_session: Session, test_dataset):
    """Test getting completed tasks."""
    # Act
    completed_tasks = task_repo.get_completed_tasks(test_session)
    
    # Assert
    assert len(completed_tasks) == 2
    for task in completed_tasks:
      assert task.status == TaskStatus.COMPLETED
  
  def test_get_completed_tasks_for_user(self, test_session: Session, test_dataset):
    """Test getting completed tasks for specific user."""
    # Arrange
    alice = test_dataset["users"]["alice"]
    
    # Act
    alice_completed = task_repo.get_completed_tasks(test_session, alice.id)
    
    # Assert
    assert len(alice_completed) == 1
    assert alice_completed[0].user_id == alice.id
    assert alice_completed[0].status == TaskStatus.COMPLETED
  
  def test_get_pending_tasks(self, test_session: Session, test_dataset):
    """Test getting pending tasks."""
    # Act
    pending_tasks = task_repo.get_pending_tasks(test_session)
    
    # Assert
    assert len(pending_tasks) == 1
    assert pending_tasks[0].status == TaskStatus.PENDING
  
  def test_mark_task_completed(self, test_session: Session, test_user: User):
    """Test marking a task as completed."""
    # Arrange
    task_create = TaskCreate(
      title="Task to complete",
      description="Will be completed",
      user_id=test_user.id
    )
    task = task_repo.create(test_session, task_create)
    assert task.status == TaskStatus.PENDING
    assert task.completed_at is None
    
    # Act
    completed_task = task_repo.mark_completed(test_session, task.id)
    
    # Assert
    assert completed_task is not None
    assert completed_task.id == task.id
    assert completed_task.status == TaskStatus.COMPLETED
    assert completed_task.completed_at is not None
    assert isinstance(completed_task.completed_at, datetime)
  
  def test_mark_nonexistent_task_completed(self, test_session: Session):
    """Test marking non-existent task as completed."""
    # Act
    result = task_repo.mark_completed(test_session, 999)
    
    # Assert
    assert result is None
  
  def test_mark_task_in_progress(self, test_session: Session, test_user: User):
    """Test marking a task as in progress."""
    # Arrange
    task_create = TaskCreate(
      title="Task to start",
      description="Will be started",
      user_id=test_user.id
    )
    task = task_repo.create(test_session, task_create)
    assert task.status == TaskStatus.PENDING
    
    # Act
    in_progress_task = task_repo.mark_in_progress(test_session, task.id)
    
    # Assert
    assert in_progress_task is not None
    assert in_progress_task.id == task.id
    assert in_progress_task.status == TaskStatus.IN_PROGRESS
  
  def test_search_by_title(self, test_session: Session, test_dataset):
    """Test searching tasks by title."""
    # Act
    task_results = task_repo.search_by_title(test_session, "Task")
    important_results = task_repo.search_by_title(test_session, "Important")
    
    # Assert
    assert len(task_results) >= 1  # Should find multiple tasks with "Task" in title
    assert len(important_results) == 1  # Only Bob's important task
    assert "Important" in important_results[0].title
  
  def test_search_by_title_for_user(self, test_session: Session, test_dataset):
    """Test searching tasks by title for specific user."""
    # Arrange
    alice = test_dataset["users"]["alice"]
    bob = test_dataset["users"]["bob"]
    
    # Act
    alice_tasks = task_repo.search_by_title(test_session, "Alice", alice.id)
    bob_tasks = task_repo.search_by_title(test_session, "Bob", bob.id)
    
    # Assert
    assert len(alice_tasks) == 2  # Both Alice's tasks have "Alice" in title
    assert len(bob_tasks) == 2    # Both Bob's tasks have "Bob" in title
    
    for task in alice_tasks:
      assert task.user_id == alice.id
    for task in bob_tasks:
      assert task.user_id == bob.id
  
  def test_update_task(self, test_session: Session, test_task: Task):
    """Test updating task fields."""
    # Arrange
    original_title = test_task.title
    original_updated_at = test_task.updated_at
    
    # Act
    update_data = TaskUpdate(
      title="Updated Task Title",
      description="Updated description",
      status=TaskStatus.IN_PROGRESS
    )
    updated_task = task_repo.update(test_session, test_task, update_data)
    
    # Assert
    assert updated_task.id == test_task.id
    assert updated_task.title == "Updated Task Title"
    assert updated_task.title != original_title
    assert updated_task.description == "Updated description"
    assert updated_task.status == TaskStatus.IN_PROGRESS
    assert updated_task.updated_at >= original_updated_at
  
  def test_delete_task(self, test_session: Session, test_task: Task):
    """Test deleting a task."""
    # Arrange
    task_id = test_task.id
    
    # Act
    deleted_task = task_repo.delete(test_session, task_id)
    
    # Assert
    assert deleted_task is not None
    assert deleted_task.id == task_id
    
    # Verify task is actually deleted
    found_task = task_repo.get(test_session, task_id)
    assert found_task is None
  
  def test_delete_nonexistent_task(self, test_session: Session):
    """Test deleting task that doesn't exist."""
    # Act
    deleted_task = task_repo.delete(test_session, 999)
    
    # Assert
    assert deleted_task is None
  
  def test_get_multi_tasks_pagination(self, test_session: Session, test_dataset):
    """Test getting multiple tasks with pagination."""
    # Act
    first_page = task_repo.get_multi(test_session, skip=0, limit=2)
    second_page = task_repo.get_multi(test_session, skip=2, limit=2)
    all_tasks = task_repo.get_multi(test_session, skip=0, limit=100)
    
    # Assert
    assert len(first_page) == 2
    assert len(second_page) >= 1  # At least 1 more task
    assert len(all_tasks) == 5  # Total tasks in test dataset
    
    # Verify no overlap between pages
    first_ids = {task.id for task in first_page}
    second_ids = {task.id for task in second_page}
    assert first_ids.isdisjoint(second_ids)
  
  def test_count_tasks(self, test_session: Session, test_dataset):
    """Test counting total tasks."""
    # Act
    count = task_repo.count(test_session)
    
    # Assert
    assert count == 5  # Total tasks in test dataset
  
  def test_task_user_relationship(self, test_session: Session, test_user: User):
    """Test task-user relationship loading."""
    # Arrange
    task_create = TaskCreate(
      title="Relationship Test Task",
      description="Testing relationships",
      user_id=test_user.id
    )
    task = task_repo.create(test_session, task_create)
    
    # Act - Get task and access user relationship
    found_task = task_repo.get(test_session, task.id)
    task_user = found_task.user
    
    # Assert
    assert task_user is not None
    assert task_user.id == test_user.id
    assert task_user.username == test_user.username