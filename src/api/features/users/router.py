"""FastAPI router for Users API endpoints."""

from typing import Dict
from uuid import UUID

from fastapi import Depends, Query
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_user_service
from src.services.users.service import UserService
from .models import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    UsersListResponse,
    UsersWithTaskCountsResponse,
)
from .controller import (
    handle_create_user,
    handle_delete_user,
    handle_get_user,
    handle_get_user_with_tasks,
    handle_get_users,
    handle_get_users_with_task_counts,
    handle_update_user,
)

users_router = APIRouter()


@users_router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create a new user."""
    return await handle_create_user(db, user_data, service)


@users_router.get("/", response_model=UsersListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    db: AsyncSession = Depends(get_db_session),
    service: UserService = Depends(get_user_service)
) -> UsersListResponse:
    """Get paginated list of users."""
    return await handle_get_users(db, service, skip=skip, limit=limit)


@users_router.get("/with-task-counts", response_model=UsersWithTaskCountsResponse)
async def get_users_with_task_counts(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    db: AsyncSession = Depends(get_db_session),
    service: UserService = Depends(get_user_service)
) -> UsersWithTaskCountsResponse:
    """Get users with their task counts."""
    return await handle_get_users_with_task_counts(db, service, limit=limit)


@users_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Get user by ID."""
    return await handle_get_user(db, user_id, service)


@users_router.get("/{user_id}/with-tasks", response_model=UserResponse)
async def get_user_with_tasks(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Get user with their tasks loaded."""
    return await handle_get_user_with_tasks(db, user_id, service)


@users_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Update user by ID."""
    return await handle_update_user(db, user_id, user_update, service)


@users_router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    service: UserService = Depends(get_user_service)
) -> Dict[str, str]:
    """Delete user by ID."""
    return await handle_delete_user(db, user_id, service)