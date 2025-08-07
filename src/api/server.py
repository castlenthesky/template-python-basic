from fastapi import FastAPI

from .features.health.router import health_router
from .middleware.cors_middleware import configure_cors_middleware

app = FastAPI(
  title="My FastAPI Application",
  description="A simple FastAPI application with health check endpoint",
  version="1.0.0",
  openapi_url="/openapi.json",
  docs_url="/docs",
)

configure_cors_middleware(app)

app.include_router(health_router, prefix="/health", tags=["Health"])


@app.get("/")
async def hello(name: str = "World"):
  return f"Hello, {name}!"
