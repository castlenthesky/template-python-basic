from sqlalchemy.ext.asyncio import AsyncSession

from src.api.features.health.models import HealthResponse
from src.services.health.service import HealthService


async def handle_health_check(db: AsyncSession, service: HealthService) -> HealthResponse:
    return await service.perform_health_check(db)
