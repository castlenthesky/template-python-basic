from datetime import datetime, timezone
from src.config import settings
from pydantic import BaseModel
from typing import Any


class HealthRequest(BaseModel):
    pass


class HealthResponse(BaseModel):
    status: str
    message: str = ""
    timestamp: datetime = datetime.now(timezone.utc)
    application: dict = {
        "application": settings.APPLICATION_NAME,
        "version": settings.APPLICATION_VERSION,
        "description": settings.APPLICATION_DESCRIPTION
    }
    api_support_documentation: dict = {
        "openapi_url": settings.API_URL + settings.APPLICATION_OPENAPI_URL,
        "docs_url": settings.API_URL + settings.APPLICATION_DOCS_URL
    }
    environment: dict = {
        "environment": settings.ENVIRONMENT,
        "is_production": settings.is_production
    }
    services: Any = None
