from src.api.features.health.models import HealthResponse
from src.services.health import health_service as service


async def handle_health_check() -> HealthResponse:
    return await service.perform_health_check()
