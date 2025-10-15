"""Controllers for Tasks API endpoints."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.tasks.service import TaskService
from .models import (
    TaskCreateRequest,
    TaskResponse,
    TaskUpdateRequest,
    TasksListResponse,
    TasksByUserResponse,
    TaskStatusUpdate,
)


async def handle_create_task(db: AsyncSession, task_data: TaskCreateRequest, service: TaskService) -> TaskResponse:
    """Create a new task."""
    task = await service.create_task(db, task_data)
    return TaskResponse.model_validate(task)


async def handle_get_task(db: AsyncSession, task_id: UUID, service: TaskService) -> TaskResponse:
    """Get task by ID."""
    task = await service.get(db, task_id)
    if not task:
        from src.services.shared.exceptions import NotFoundError
        raise NotFoundError(f"Task with ID {task_id} not found")
    return TaskResponse.model_validate(task)


async def handle_get_tasks(db: AsyncSession, service: TaskService, skip: int = 0, limit: int = 100) -> TasksListResponse:
    """Get paginated list of tasks."""
    tasks = await service.get_multi(db, skip=skip, limit=limit)
    # Note: In production, you'd want to get actual total count
    return TasksListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
        skip=skip,
        limit=limit,
    )


async def handle_get_tasks_by_user(
    db: AsyncSession, user_id: UUID, service: TaskService, skip: int = 0, limit: int = 100
) -> TasksByUserResponse:
    """Get tasks for a specific user."""
    tasks = await service.get_tasks_by_user(db, user_id, skip=skip, limit=limit)
    return TasksByUserResponse(
        user_id=user_id,
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
    )


async def handle_update_task(
    db: AsyncSession, task_id: UUID, task_update: TaskUpdateRequest, service: TaskService
) -> TaskResponse:
    """Update task by ID."""
    # First get the task to ensure it exists
    task = await service.get(db, task_id)
    if not task:
        from src.services.shared.exceptions import NotFoundError
        raise NotFoundError(f"Task with ID {task_id} not found")
    
    # Update the task (this would need to be implemented in the service layer)
    # For now, we'll return the existing task with the note that update needs implementation
    # TODO: Implement update functionality in service layer
    _ = task_update  # Acknowledge parameter to avoid unused warning
    return TaskResponse.model_validate(task)


async def handle_update_task_status(
    db: AsyncSession, task_id: UUID, status_update: TaskStatusUpdate, service: TaskService
) -> TaskResponse:
    """Update task status."""
    task = await service.update_task_status(db, task_id, status_update.status)
    if not task:
        from src.services.shared.exceptions import NotFoundError
        raise NotFoundError(f"Task with ID {task_id} not found")
    return TaskResponse.model_validate(task)


async def handle_delete_task(db: AsyncSession, task_id: UUID, service: TaskService) -> dict:
    """Delete task by ID."""
    deleted_task = await service.delete(db, task_id)
    if not deleted_task:
        from src.services.shared.exceptions import NotFoundError
        raise NotFoundError(f"Task with ID {task_id} not found")
    
    return {"message": f"Task '{deleted_task.title}' deleted successfully"}


async def handle_get_overdue_tasks(
    db: AsyncSession, service: TaskService, skip: int = 0, limit: int = 100
) -> TasksListResponse:
    """Get overdue tasks."""
    tasks = await service.get_overdue_tasks(db, skip=skip, limit=limit)
    return TasksListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
        skip=skip,
        limit=limit,
    )


async def handle_get_tasks_by_priority(
    db: AsyncSession, priority: int, service: TaskService, skip: int = 0, limit: int = 100
) -> TasksListResponse:
    """Get tasks by priority level."""
    tasks = await service.get_tasks_by_priority(db, priority, skip=skip, limit=limit)
    return TasksListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
        skip=skip,
        limit=limit,
    )