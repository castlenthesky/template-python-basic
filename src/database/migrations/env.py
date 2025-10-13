"""Alembic environment configuration for async-first architecture.

This file configures Alembic to run migrations for SQLModel-based models.
It supports async database connections (e.g., PostgreSQL with asyncpg) and
offline mode for generating migration scripts without a database connection.
Ensure `settings.DATABASE_URL` is set (e.g., 'postgresql+asyncpg://...') and
all models are imported via `src.database.models` for auto-detection.
"""

import asyncio
import logging
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import models to register with SQLModel.metadata
from sqlmodel import SQLModel

from src.config import settings

# Add project root to sys.path for model imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


logger = logging.getLogger(__name__)

# Alembic Config object
config = context.config

# Override database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
  fileConfig(config.config_file_name)

# Set metadata for autogenerate
target_metadata = SQLModel.metadata


def do_run_migrations(connection):
  """Run migrations with the provided connection."""
  context.configure(
    connection=connection,
    target_metadata=target_metadata,
    compare_type=True,  # Detect column type changes
    compare_server_default=True,  # Detect server default changes
    include_schemas=True,  # Support schema (e.g., 'public')
    render_as_batch=True,  # Support batch operations for SQLite, etc.
  )

  with context.begin_transaction():
    logger.info("Starting migration execution")
    context.run_migrations()
    logger.info("Migration execution completed")


async def run_async_migrations():
  """Run migrations in async mode."""
  logger.info("Initializing async migrations")

  try:
    connectable = async_engine_from_config(
      config.get_section(config.config_ini_section) or {},
      prefix="sqlalchemy.",
      poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
      logger.info("Database connection established")
      await connection.run_sync(do_run_migrations)

    await connectable.dispose()
    logger.info("Database connection closed")

  except Exception as e:
    logger.error(f"Migration failed: {str(e)}")
    raise


def run_migrations_offline() -> None:
  """Run migrations in offline mode.

  Generates migration scripts without connecting to the database.
  Useful for CI/CD or environments without DB access.
  """
  url = config.get_main_option("sqlalchemy.url")
  if not url:
    raise ValueError("Database URL not configured")
  dialect = make_url(url).drivername.split("+")[0]  # Robust dialect extraction
  logger.info(f"Running offline migrations for {dialect} database")

  context.configure(
    url=url,
    target_metadata=target_metadata,
    literal_binds=True,
    dialect_opts={"paramstyle": "named"},
    compare_type=True,
    compare_server_default=True,
    include_schemas=True,  # Support schema
    render_as_batch=True,  # Support batch operations
  )

  with context.begin_transaction():
    context.run_migrations()


def run_migrations_online() -> None:
  """Run migrations in online async mode."""
  url = config.get_main_option("sqlalchemy.url")
  if not url:
    raise ValueError("Database URL not configured")
  dialect = make_url(url).drivername.split("+")[0]
  logger.info(f"Running async migrations for {dialect} database")
  asyncio.run(run_async_migrations())


if context.is_offline_mode():
  run_migrations_offline()
else:
  run_migrations_online()
