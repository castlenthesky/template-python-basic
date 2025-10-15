"""Request and response models for Tasks API."""

from typing import List
from uuid import UUID

from pydantic import BaseModel

from src.database.models.public.task import TaskCreate as TaskCreateDB
from src.database.models.public.task import TaskRead as TaskReadDB
from src.database.models.public.task import TaskUpdate as TaskUpdateDB
from src.database.models.public.task import TaskStatus


class TaskCreateRequest(TaskCreateDB):
    """Request model for creating a task."""
    
    pass


class TaskUpdateRequest(TaskUpdateDB):
    """Request model for updating a task."""
    
    pass


class TaskResponse(TaskReadDB):
    """Response model for task data."""
    
    pass


class TasksListResponse(BaseModel):
    """Response model for list of tasks."""
    
    tasks: List[TaskResponse]
    total: int
    skip: int
    limit: int


class TasksByUserResponse(BaseModel):
    """Response model for tasks filtered by user."""
    
    user_id: UUID
    tasks: List[TaskResponse]
    total: int


class TaskStatusUpdate(BaseModel):
    """Request model for updating task status only."""
    
    status: TaskStatus