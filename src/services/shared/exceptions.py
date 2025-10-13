"""Shared exceptions for services."""


class ServiceError(Exception):
    """Base exception for service layer errors."""
    pass


class NotFoundError(ServiceError):
    """Raised when a resource is not found."""
    pass


class ValidationError(ServiceError):
    """Raised when validation fails."""
    pass


class DuplicateError(ServiceError):
    """Raised when attempting to create a duplicate resource."""
    pass