"""Alembic environment configuration for async-first architecture."""

import asyncio
import logging
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# Add the project root to the path so we can import our models
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our settings and models
from src.config import settings
from src.database.models.task import Task
from src.database.models.user import User
from sqlmodel import SQLModel

logger = logging.getLogger(__name__)

# This is the Alembic Config object
config = context.config

# Override URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
# Import models to ensure they're registered with SQLModel metadata
_ = User, Task
target_metadata = SQLModel.metadata


def do_run_migrations(connection):
    """Run migrations with the provided connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Run migrations in async mode."""
    logger.info("Running async migrations")
    
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' async mode."""
    database_url = config.get_main_option("sqlalchemy.url")
    from urllib.parse import urlparse
    dialect = urlparse(database_url).scheme.split("+")[0]
    
    logger.info(f"Running async migrations for {dialect} database")
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
