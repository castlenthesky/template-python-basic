"""Application configuration settings."""

from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
  # Legacy test setting
  TEST: str = "UNCONFIGURED"

  # Database settings
  DATABASE_URL: Optional[str] = None
  # DATABASE_CONNECTION_STRING: str = "sqlite:///data/app_sqlite.db"
  DATABASE_CONNECTION_STRING: str = "duckdb:///app.db"
  SQL_ECHO: bool = False

  # Database connection pool settings
  DATABASE_POOL_SIZE: int = 5
  DATABASE_MAX_OVERFLOW: int = 10
  DATABASE_POOL_TIMEOUT: int = 30
  DATABASE_POOL_RECYCLE: int = 3600

  class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"
    extra = "allow"

  def get_database_url(self) -> str:
    """Get database URL with fallback priority: DATABASE_URL > DATABASE_CONNECTION_STRING > default SQLite."""
    if self.DATABASE_URL:
      return self.DATABASE_URL

    if self.DATABASE_CONNECTION_STRING:
      return self.DATABASE_CONNECTION_STRING

    # Default to local SQLite file in project data directory
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "data" / "app.db"
    db_path.parent.mkdir(exist_ok=True)

    return f"sqlite:///{db_path}"

  def get_database_type(self) -> str:
    """Get database type from connection string."""
    url = self.get_database_url()
    return urlparse(url).scheme.split("+")[0]


settings = Settings()
