"""User-specific exceptions."""

from ..shared.exceptions import ServiceError


class UserError(ServiceError):
    """Base exception for user-related errors."""
    pass


class UserNotFoundError(UserError):
    """Raised when a user is not found."""
    pass


class UserAlreadyExistsError(UserError):
    """Raised when attempting to create a user that already exists."""
    pass