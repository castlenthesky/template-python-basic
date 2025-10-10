"""Async database connection and health check utilities."""

import logging
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from ..config import settings
from .engine import get_global_async_engine

logger = logging.getLogger(__name__)


class AsyncDatabaseConnection:
    """Async database connection utilities and health checks."""
    
    def __init__(self, async_engine_override: Optional[AsyncEngine] = None):
        """Initialize with optional async engine override."""
        self._async_engine = async_engine_override
        self._session_factory = None
    
    @property
    def engine(self) -> AsyncEngine:
        """Get the asynchronous database engine."""
        if self._async_engine is None:
            self._async_engine = get_global_async_engine()
        return self._async_engine
    
    def create_session(self) -> AsyncSession:
        """Create a new asynchronous database session."""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._session_factory()
    
    async def health_check(self) -> bool:
        """Check database connectivity and health."""
        try:
            async with self.create_session() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information."""
        engine = self.engine
        url_str = str(engine.url)
        
        # Mask password if present
        if engine.url.password:
            url_str = url_str.replace(str(engine.url.password), "***")

        return {
            "url": url_str,
            "driver": engine.name,
            "dialect": settings.get_database_type(),
            "pool_size": getattr(engine.pool, "size", None),
            "checked_out_connections": getattr(engine.pool, "checkedout", None),
            "overflow_connections": getattr(engine.pool, "overflow", None),
            "checked_in_connections": getattr(engine.pool, "checkedin", None),
        }
    
    async def close_connections(self) -> None:
        """Close all database connections."""
        if self._async_engine is not None:
            await self._async_engine.dispose()
            logger.info("Database connections closed")


# Global async database connection instance (lazy loaded)
_async_db_connection = None

def get_async_db_connection() -> AsyncDatabaseConnection:
    """Get global async database connection (lazy loaded)."""
    global _async_db_connection
    if _async_db_connection is None:
        _async_db_connection = AsyncDatabaseConnection()
    return _async_db_connection


# Aliases for convenience
db_connection = get_async_db_connection
get_db_connection = get_async_db_connection
