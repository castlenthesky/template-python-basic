"""Controllers for Users API endpoints."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.users.service import UserService
from .models import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    UsersListResponse,
    UsersWithTaskCountsResponse,
    UserWithTaskCountResponse,
)


async def handle_create_user(db: AsyncSession, user_data: UserCreateRequest, service: UserService) -> UserResponse:
    """Create a new user."""
    user = await service.create_user(db, user_data)
    return UserResponse.model_validate(user)


async def handle_get_user(db: AsyncSession, user_id: UUID, service: UserService) -> UserResponse:
    """Get user by ID."""
    user = await service.get(db, user_id)
    if not user:
        from src.services.shared.exceptions import NotFoundError
        raise NotFoundError(f"User with ID {user_id} not found")
    return UserResponse.model_validate(user)


async def handle_get_users(db: AsyncSession, service: UserService, skip: int = 0, limit: int = 100) -> UsersListResponse:
    """Get paginated list of users."""
    users = await service.get_multi(db, skip=skip, limit=limit)
    # Note: In production, you'd want to get actual total count
    # For now, we'll use the length of returned users as an approximation
    return UsersListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=len(users),
        skip=skip,
        limit=limit,
    )


async def handle_update_user(
    db: AsyncSession, user_id: UUID, user_update: UserUpdateRequest, service: UserService
) -> UserResponse:
    """Update user by ID."""
    updated_user = await service.update_user(db, user_id, user_update)
    return UserResponse.model_validate(updated_user)


async def handle_delete_user(db: AsyncSession, user_id: UUID, service: UserService) -> dict:
    """Delete user by ID."""
    deleted_user = await service.delete(db, user_id)
    if not deleted_user:
        from src.services.shared.exceptions import NotFoundError
        raise NotFoundError(f"User with ID {user_id} not found")
    
    return {"message": f"User {deleted_user.username} deleted successfully"}


async def handle_get_user_with_tasks(db: AsyncSession, user_id: UUID, service: UserService) -> UserResponse:
    """Get user with their tasks loaded."""
    user = await service.get_user_with_tasks(db, user_id)
    if not user:
        from src.services.shared.exceptions import NotFoundError
        raise NotFoundError(f"User with ID {user_id} not found")
    return UserResponse.model_validate(user)


async def handle_get_users_with_task_counts(
    db: AsyncSession, service: UserService, limit: int = 100
) -> UsersWithTaskCountsResponse:
    """Get users with their task counts."""
    users_with_counts = await service.get_users_with_task_counts(db, limit=limit)
    
    user_responses = [
        UserWithTaskCountResponse(
            user=UserResponse.model_validate(user), 
            task_count=count
        )
        for user, count in users_with_counts
    ]
    
    return UsersWithTaskCountsResponse(
        users=user_responses,
        total=len(user_responses),
    )