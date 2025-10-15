from sqlalchemy.ext.asyncio import AsyncSession

from src.api.features.health.models import HealthResponse
from src.services.health import health_service as service


async def handle_health_check(db: AsyncSession) -> HealthResponse:
    return await service.perform_health_check(db)
