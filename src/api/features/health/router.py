from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_health_service
from src.services.health.service import HealthService
from src.api.features.health.models import HealthResponse

from .controller import handle_health_check

health_router = APIRouter()


@health_router.get("/", name="health_check", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_db_session),
    service: HealthService = Depends(get_health_service)
) -> HealthResponse:
    return await handle_health_check(db, service)
