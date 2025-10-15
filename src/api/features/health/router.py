from fastapi.routing import APIRouter

from src.api.features.health.models import HealthResponse

from .controller import handle_health_check

health_router = APIRouter()


@health_router.get("/", name="health_check", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return await handle_health_check()
