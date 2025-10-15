"""Health service for application health checks."""

import logging
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.features.health.models import HealthResponse
from src.config import settings

logger = logging.getLogger(__name__)


class HealthService:
    """Health service for performing application health checks."""
    
    async def perform_health_check(self, db: Optional[AsyncSession] = None) -> HealthResponse:
        """
        Perform health check and return status.
        
        Args:
            db: Database session for performing health checks
            
        Returns:
            HealthResponse with status and message
        """
        try:
            # Perform database health check
            db_healthy = True
            db_error = None
            
            if db:
                try:
                    # Simple database connectivity test
                    result = await db.execute(text("SELECT 1"))
                    result.fetchone()
                    logger.info(f"Database health check passed - Environment: {settings.ENVIRONMENT}")
                except Exception as e:
                    db_healthy = False
                    db_error = str(e)
                    logger.warning(f"Database health check failed: {e}")
            
            # Determine overall status
            if db_healthy:
                status = "healthy"
                message = "Service is running smoothly"
            else:
                status = "degraded"  
                message = f"Service running but database issues detected"
            
            return HealthResponse(
                status=status,
                message=message,
                details={
                    "environment": settings.ENVIRONMENT,
                    "is_production": settings.is_production,
                    "database_healthy": db_healthy,
                    "database_error": db_error if not db_healthy else None,
                    "version": "1.0.0",
                }
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthResponse(
                status="error",
                message=f"Health check failed: {str(e)}"
            )