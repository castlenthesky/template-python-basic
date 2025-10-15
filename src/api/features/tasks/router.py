"""FastAPI router for Tasks API endpoints."""

from typing import Dict
from uuid import UUID

from fastapi import Depends, Query
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_task_service
from src.services.tasks.service import TaskService
from .models import (
    TaskCreateRequest,
    TaskResponse,
    TaskUpdateRequest,
    TasksListResponse,
    TasksByUserResponse,
    TaskStatusUpdate,
)
from .controller import (
    handle_create_task,
    handle_delete_task,
    handle_get_task,
    handle_get_tasks,
    handle_get_tasks_by_priority,
    handle_get_tasks_by_user,
    handle_get_overdue_tasks,
    handle_update_task,
    handle_update_task_status,
)

tasks_router = APIRouter()


@tasks_router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """Create a new task."""
    return await handle_create_task(db, task_data, service)


@tasks_router.get("/", response_model=TasksListResponse)
async def get_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks to return"),
    db: AsyncSession = Depends(get_db_session),
    service: TaskService = Depends(get_task_service)
) -> TasksListResponse:
    """Get paginated list of tasks."""
    return await handle_get_tasks(db, service, skip=skip, limit=limit)


@tasks_router.get("/overdue", response_model=TasksListResponse)
async def get_overdue_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks to return"),
    db: AsyncSession = Depends(get_db_session),
    service: TaskService = Depends(get_task_service)
) -> TasksListResponse:
    """Get overdue tasks."""
    return await handle_get_overdue_tasks(db, service, skip=skip, limit=limit)


@tasks_router.get("/priority/{priority}", response_model=TasksListResponse)
async def get_tasks_by_priority(
    priority: int,
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks to return"),
    db: AsyncSession = Depends(get_db_session),
    service: TaskService = Depends(get_task_service)
) -> TasksListResponse:
    """Get tasks by priority level."""
    return await handle_get_tasks_by_priority(db, priority, service, skip=skip, limit=limit)


@tasks_router.get("/user/{user_id}", response_model=TasksByUserResponse)
async def get_tasks_by_user(
    user_id: UUID,
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks to return"),
    db: AsyncSession = Depends(get_db_session),
    service: TaskService = Depends(get_task_service)
) -> TasksByUserResponse:
    """Get tasks for a specific user."""
    return await handle_get_tasks_by_user(db, user_id, service, skip=skip, limit=limit)


@tasks_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """Get task by ID."""
    return await handle_get_task(db, task_id, service)


@tasks_router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """Update task by ID."""
    return await handle_update_task(db, task_id, task_update, service)


@tasks_router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: UUID,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db_session),
    service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """Update task status."""
    return await handle_update_task_status(db, task_id, status_update, service)


@tasks_router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    service: TaskService = Depends(get_task_service)
) -> Dict[str, str]:
    """Delete task by ID."""
    return await handle_delete_task(db, task_id, service)