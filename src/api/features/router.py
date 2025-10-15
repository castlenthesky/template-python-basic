from fastapi import APIRouter

from src.api.features.health.router import health_router
from src.api.features.users.router import users_router
from src.api.features.tasks.router import tasks_router
from src.api.features.guide.router import guide_router

router = APIRouter()

router.include_router(health_router, prefix="/health", tags=["Health"])
router.include_router(guide_router, prefix="/guide", tags=["Guide"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])