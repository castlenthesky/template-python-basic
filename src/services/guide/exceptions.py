"""Custom exceptions for guide service."""


class DocumentNotFoundError(Exception):
    """Raised when a requested document cannot be found."""
    pass


class InvalidPathError(Exception):
    """Raised when an invalid or unsafe path is provided."""
    pass