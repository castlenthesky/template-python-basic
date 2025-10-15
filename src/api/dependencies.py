"""FastAPI dependencies for dependency injection."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_db_connection
from src.services.users.service import UserService
from src.services.users.repository import UserRepository
from src.services.tasks.service import TaskService
from src.services.tasks.repository import TaskRepository
from src.services.health.service import HealthService
from src.services.guide.service import DocumentService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to provide async database session."""
    db_connection = get_async_db_connection()
    session = db_connection.create_session()
    try:
        yield session
    finally:
        await session.close()


def get_user_repository() -> UserRepository:
    """Dependency to provide user repository."""
    return UserRepository()


def get_user_service() -> UserService:
    """Dependency to provide user service with repository dependency."""
    return UserService(get_user_repository())


def get_task_repository() -> TaskRepository:
    """Dependency to provide task repository."""
    return TaskRepository()


def get_task_service() -> TaskService:
    """Dependency to provide task service with repository dependency."""
    return TaskService(get_task_repository())


def get_health_service() -> HealthService:
    """Dependency to provide health service."""
    return HealthService()


def get_document_service() -> DocumentService:
    """Dependency to provide document service."""
    return DocumentService()