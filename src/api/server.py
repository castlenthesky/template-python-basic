import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.features.health.router import health_router
from src.api.middleware.cors_middleware import configure_cors_middleware
from src.database import get_async_db_connection

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
    title="My FastAPI Application",
    description="A simple FastAPI application with health check endpoint",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    lifespan=lifespan,
)

configure_cors_middleware(app)

app.include_router(health_router, prefix="/health", tags=["Health"])


@app.get("/")
async def hello(name: str = "World"):
    return f"Hello, {name}!"
