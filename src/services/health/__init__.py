"""Health service module."""

from .service import HealthService

health_service = HealthService()

__all__ = ["HealthService", "health_service"]