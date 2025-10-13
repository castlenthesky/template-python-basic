"""Task-specific exceptions."""

from ..shared.exceptions import ServiceError


class TaskError(ServiceError):
    """Base exception for task-related errors."""
    pass


class TaskNotFoundError(TaskError):
    """Raised when a task is not found."""
    pass


class InvalidTaskStatusError(TaskError):
    """Raised when an invalid task status transition is attempted."""
    pass