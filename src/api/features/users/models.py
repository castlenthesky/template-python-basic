"""Request and response models for Users API."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from src.database.models.public.user import UserCreate as UserCreateDB
from src.database.models.public.user import UserRead as UserReadDB
from src.database.models.public.user import UserUpdate as UserUpdateDB


class UserCreateRequest(UserCreateDB):
    """Request model for creating a user."""
    
    pass


class UserUpdateRequest(UserUpdateDB):
    """Request model for updating a user."""
    
    pass


class UserResponse(UserReadDB):
    """Response model for user data."""
    
    pass


class UsersListResponse(BaseModel):
    """Response model for list of users."""
    
    users: List[UserResponse]
    total: int
    skip: int
    limit: int


class UserWithTaskCountResponse(BaseModel):
    """Response model for user with task count."""
    
    user: UserResponse
    task_count: int


class UsersWithTaskCountsResponse(BaseModel):
    """Response model for users with task counts."""
    
    users: List[UserWithTaskCountResponse]
    total: int