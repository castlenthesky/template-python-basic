from pydantic import BaseModel
from typing import Any


class HealthRequest(BaseModel):
    pass


class HealthResponse(BaseModel):
    status: str
    message: str = ""
    details: Any = None
