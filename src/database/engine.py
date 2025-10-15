"""Async database engine configuration."""

import logging
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

from ..config import settings

logger = logging.getLogger(__name__)


def _get_async_engine_config() -> dict:
    """Get async engine configuration for async-first applications."""
    database_type = settings.get_database_type()
    
    # Base configuration for async engines
    engine_kwargs = {
        "echo": settings.SQL_ECHO,
        "pool_pre_ping": True,
        "pool_recycle": settings.DATABASE_POOL_RECYCLE,
    }
    
    # Database-specific configurations
    if database_type == "sqlite":
        # For async SQLite, use NullPool to avoid threading issues
        engine_kwargs.update({
            "poolclass": NullPool,
        })
    else:
        # PostgreSQL, MySQL - use SQLAlchemy's default async pooling
        # Don't specify poolclass - let SQLAlchemy handle async-compatible pooling
        pass
    
    return engine_kwargs


@lru_cache(maxsize=1)
def get_async_engine() -> AsyncEngine:
    """Create and cache the asynchronous database engine."""
    database_url = settings.DATABASE_URL
    database_type = settings.get_database_type()
    
    engine_kwargs = _get_async_engine_config()
    engine = create_async_engine(database_url, **engine_kwargs)
    
    logger.info(f"Created async {database_type} engine")
    return engine


def create_async_engine_for_url(database_url: str) -> AsyncEngine:
    """Create async engine for a specific database URL (useful for testing)."""
    # Validate async driver
    async_drivers = {"+asyncpg", "+aiomysql", "+aiosqlite"}
    if not any(driver in database_url for driver in async_drivers):
        raise ValueError(
            f"Database URL must use async driver. Got: {database_url}. "
            f"Supported: postgresql+asyncpg, mysql+aiomysql, sqlite+aiosqlite"
        )
    
    from urllib.parse import urlparse
    database_type = urlparse(database_url).scheme.split("+")[0]
    
    # Configure engine based on type - async-first approach
    engine_kwargs = {
        "echo": settings.SQL_ECHO,
        "pool_pre_ping": True,
        "pool_recycle": settings.DATABASE_POOL_RECYCLE,
    }
    
    if database_type == "sqlite":
        engine_kwargs["poolclass"] = NullPool
    else:
        # For PostgreSQL/MySQL - let SQLAlchemy handle async pooling
        pass
    
    return create_async_engine(database_url, **engine_kwargs)


# Global async engine instance (lazy loaded)
_async_engine = None

def get_global_async_engine() -> AsyncEngine:
    """Get global async engine instance (lazy loaded)."""
    global _async_engine
    if _async_engine is None:
        _async_engine = get_async_engine()
    return _async_engine


# Alias for backwards compatibility
async_engine = get_global_async_engine
