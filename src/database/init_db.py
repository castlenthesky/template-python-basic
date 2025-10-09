"""Database initialization utilities with database-agnostic support."""

from sqlmodel import SQLModel

from src.database.engine import engine
from src.database.models.task import Task
from src.database.models.user import User


def create_tables():
  """Create all database tables."""
  print("Creating database tables...")

  # Import models to ensure they're registered with SQLModel metadata
  _ = User, Task

  # Create all tables
  SQLModel.metadata.create_all(engine)

  print("✅ Database tables created successfully!")


def drop_tables():
  """Drop all database tables (use with caution!)."""
  print("Dropping all database tables...")

  # Import models to ensure they're registered with SQLModel metadata
  _ = User, Task

  # Drop all tables
  SQLModel.metadata.drop_all(engine)

  print("✅ Database tables dropped successfully!")


def reset_database():
  """Reset database by dropping and recreating all tables."""
  print("Resetting database...")
  drop_tables()
  create_tables()
  print("✅ Database reset completed!")


if __name__ == "__main__":
  """Run database initialization when script is executed directly."""
  import sys

  if len(sys.argv) > 1 and sys.argv[1] == "--reset":
    reset_database()
  else:
    create_tables()
