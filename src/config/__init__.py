"""Application configuration settings for async-first architecture."""

from pathlib import Path
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  """Application settings for async database operations."""

  # Environment test setting
  TEST: str = "UNCONFIGURED"

  # Database settings - async drivers only
  DATABASE_URL: str = ""  # Required, will be set in constructor if empty
  SQL_ECHO: bool = False

  # Async database connection pool settings
  DATABASE_POOL_SIZE: int = 5
  DATABASE_MAX_OVERFLOW: int = 10
  DATABASE_POOL_TIMEOUT: int = 30
  DATABASE_POOL_RECYCLE: int = 3600

  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="allow",
  )

  def __init__(self, **values):
    """Initialize settings with async SQLite fallback for development."""
    super().__init__(**values)

    # Fallback to async SQLite if no URL provided (development only)
    if not self.DATABASE_URL:
      project_root = Path(__file__).parent.parent.parent
      db_path = project_root / "data" / "app.db"
      db_path.parent.mkdir(exist_ok=True)
      self.DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

  def get_database_type(self) -> str:
    """Get database type from connection string."""
    return urlparse(self.DATABASE_URL).scheme.split("+")[0]

  def validate_async_database(self) -> None:
    """Validate that database URL uses async driver."""
    async_drivers = {"+asyncpg", "+aiomysql", "+aiosqlite"}
    if not any(driver in self.DATABASE_URL for driver in async_drivers):
      raise ValueError(
        f"Database URL must use async driver. Got: {self.DATABASE_URL}. "
        f"Supported async drivers: postgresql+asyncpg, mysql+aiomysql, sqlite+aiosqlite"
      )


settings = Settings()

# Validate async configuration on import
settings.validate_async_database()
