"""Database engine configuration with database-agnostic support."""

from functools import lru_cache
from sqlalchemy import create_engine, Engine
from sqlalchemy.pool import StaticPool, QueuePool
from ..config import settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
  """Create and cache database engine with database-agnostic configuration."""
  database_url = settings.get_database_url()
  database_type = settings.get_database_type()
  
  # Base configuration for all databases
  engine_kwargs = {
    "echo": settings.SQL_ECHO,
    "pool_pre_ping": True,
    "pool_recycle": settings.DATABASE_POOL_RECYCLE,
  }
  
  # Database-specific configurations
  if database_type in ["sqlite"]:
    # SQLite-specific configuration
    engine_kwargs.update({
      "poolclass": StaticPool,
      "connect_args": {
        "check_same_thread": False,  # Allow multiple threads
        "timeout": 30,  # Connection timeout in seconds
      }
    })
  else:
    # PostgreSQL, MySQL, DuckDB, and other databases
    engine_kwargs.update({
      "poolclass": QueuePool,
      "pool_size": settings.DATABASE_POOL_SIZE,
      "max_overflow": settings.DATABASE_MAX_OVERFLOW,
      "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
    })
  
  return create_engine(database_url, **engine_kwargs)


# Global engine instance
engine = get_engine()