"""
Hello World example demonstrating SQLAlchemy + SQLite with SQLModel.

This example showcases:
- Database connection and session management
- Creating users and tasks
- Using repository pattern for CRUD operations
- Proper session handling with context managers
- Error handling and transactions
"""

from sqlmodel import SQLModel

from src.database.engine import engine
from src.database.models.task import TaskCreate
from src.database.models.user import UserCreate, UserRead
from src.database.operations.task_ops import task_repo
from src.database.operations.user_ops import user_repo
from src.database.session import get_session, session_scope


def create_tables():
  """Create all database tables."""
  print("Creating database tables...")
  SQLModel.metadata.create_all(engine)
  print("✅ Tables created successfully!")


def hello_world_example():
  """Main hello world example function."""

  print("\n🚀 SQLAlchemy + SQLite Hello World Example")
  print("=" * 50)

  # Create tables first
  create_tables()

  # Example 1: Using session_scope context manager
  print("\n📝 Example 1: Creating users and tasks")

  with session_scope() as session:
    try:
      # Create a user
      user_create = UserCreate(username="john_doe")
      user = user_repo.create_user(session, user_create)
      print(f"✅ Created user: {user}")

      # Create tasks for the user
      task_creates = [
        TaskCreate(
          title="Learn SQLAlchemy", description="Master the art of SQL in Python", user_id=user.id
        ),
        TaskCreate(
          title="Build awesome app",
          description="Create something amazing with DuckDB",
          user_id=user.id,
        ),
        TaskCreate(
          title="Write documentation",
          description="Document the awesome new features",
          user_id=user.id,
        ),
      ]

      tasks = []
      for task_create in task_creates:
        task = task_repo.create(session, task_create)
        tasks.append(task)
        print(f"✅ Created task: {task}")

    except Exception as e:
      print(f"❌ Error in Example 1: {e}")
      raise

  # Example 2: Reading and updating data
  print("\n📖 Example 2: Reading and updating data")

  with session_scope() as session:
    try:
      # Find user by username
      user = user_repo.get_by_username(session, "john_doe")
      if user:
        print(f"🔍 Found user: {user}")

        # Get user's tasks
        user_tasks = task_repo.get_by_user(session, user.id)
        print(f"📋 User has {len(user_tasks)} tasks:")
        for task in user_tasks:
          print(f"  - {task}")

        # Mark first task as completed
        if user_tasks:
          completed_task = task_repo.mark_completed(session, user_tasks[0].id)
          print(f"✅ Completed task: {completed_task}")

          # Mark second task as in progress
          if len(user_tasks) > 1:
            in_progress_task = task_repo.mark_in_progress(session, user_tasks[1].id)
            print(f"🔄 Started task: {in_progress_task}")

    except Exception as e:
      print(f"❌ Error in Example 2: {e}")
      raise

  # Example 3: Advanced queries and filtering
  print("\n🔍 Example 3: Advanced queries and filtering")

  with session_scope() as session:
    try:
      # Get all users
      all_users = user_repo.get_multi(session, limit=10)
      print(f"👥 Total users: {len(all_users)}")

      # Get completed tasks
      completed_tasks = task_repo.get_completed_tasks(session)
      print(f"✅ Completed tasks: {len(completed_tasks)}")

      # Get pending tasks
      pending_tasks = task_repo.get_pending_tasks(session)
      print(f"⏳ Pending tasks: {len(pending_tasks)}")

      # Search tasks by title
      search_results = task_repo.search_by_title(session, "awesome")
      print(f"🔎 Tasks with 'awesome': {len(search_results)}")

      # Get user with tasks (relationship loading)
      user = user_repo.get_user_with_tasks(session, all_users[0].id)
      if user:
        print(f"👤 User with tasks loaded: {user.username} ({len(user.tasks)} tasks)")

    except Exception as e:
      print(f"❌ Error in Example 3: {e}")
      raise

  # Example 4: Using FastAPI dependency injection pattern
  print("\n🌐 Example 4: FastAPI dependency injection pattern")

  def simulate_api_endpoint():
    """Simulate how this would work in a FastAPI endpoint."""
    # This simulates: def get_users(session: Session = Depends(get_session)):
    session_gen = get_session()
    session = next(session_gen)

    try:
      users = user_repo.get_multi(session, limit=5)
      return [UserRead.model_validate(user) for user in users]
    except Exception:
      session.rollback()
      raise
    finally:
      session.close()

  try:
    api_users = simulate_api_endpoint()
    print(f"🌐 API returned {len(api_users)} users")
    for user in api_users:
      print(f"  - API User: {user.username} (ID: {user.id})")
  except Exception as e:
    print(f"❌ Error in Example 4: {e}")

  print("\n🎉 Hello World example completed successfully!")
  print("=" * 50)


def cleanup_example_data():
  """Clean up example data."""
  print("\n🧹 Cleaning up example data...")

  with session_scope() as session:
    try:
      # Get all users (this will cascade delete their tasks)
      users = user_repo.get_multi(session)
      for user in users:
        user_repo.delete(session, user.id)
        print(f"🗑️ Deleted user: {user.username}")

    except Exception as e:
      print(f"❌ Error during cleanup: {e}")
      raise

  print("✅ Cleanup completed!")


if __name__ == "__main__":
  """Run the hello world example when script is executed directly."""
  try:
    hello_world_example()

    # Ask user if they want to clean up (handle non-interactive environments)
    try:
      response = input("\nDo you want to clean up the example data? (y/N): ")
      if response.lower().startswith("y"):
        cleanup_example_data()
      else:
        print("Example data retained for inspection.")
    except EOFError:
      print("Running in non-interactive mode. Example data retained for inspection.")

  except Exception as e:
    print(f"\n💥 Fatal error: {e}")
    raise
