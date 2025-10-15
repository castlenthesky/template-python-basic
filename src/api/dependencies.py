"""FastAPI dependencies for dependency injection."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_db_connection


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to provide async database session."""
    db_connection = get_async_db_connection()
    session = db_connection.create_session()
    try:
        yield session
    finally:
        await session.close()