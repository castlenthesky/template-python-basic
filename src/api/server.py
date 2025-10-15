import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.features.health.router import health_router
from src.api.features.users.router import users_router
from src.api.features.tasks.router import tasks_router
from src.api.features.guide.router import guide_router
from src.api.middleware.cors_middleware import configure_cors_middleware
from src.api.middleware.error_handling import configure_error_handling
from src.database import get_async_db_connection
from src.config import settings
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup: Initialize database connection pool
    logger.info("Starting up: Initializing database connection")
    db_connection = get_async_db_connection()
    
    # Test database connectivity
    if await db_connection.health_check():
        logger.info("Database connection established successfully")
    else:
        logger.warning("Database connection failed during startup")
    
    yield
    
    # Shutdown: Clean up database connections
    logger.info("Shutting down: Cleaning up database connections")
    await db_connection.close_connections()


app = FastAPI(
    title=settings.APPLICATION_NAME,
    description=settings.APPLICATION_DESCRIPTION,
    version=settings.APPLICATION_VERSION,
    openapi_url=settings.APPLICATION_OPENAPI_URL,
    docs_url=settings.APPLICATION_DOCS_URL,
    lifespan=lifespan,
)

configure_cors_middleware(app)
configure_error_handling(app)

app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
app.include_router(guide_router, prefix="/guide", tags=["Guide"])


@app.get("/")
async def hello():
    return f"Hello, from {settings.APPLICATION_NAME}!"
