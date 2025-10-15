"""Application configuration settings for async-first architecture."""

from pathlib import Path
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  """Application settings for async database operations."""

  model_config = SettingsConfigDict(
      env_file=".env",
      env_file_encoding="utf-8",
      extra="allow",
  )

  # Application Settings
  ENVIRONMENT_PROPOGATION_VALUE: str = "UNCONFIGURED"
  ENVIRONMENT: str = "development"

  API_PORT: int = 8000
  API_URL: str = "http://localhost:8000"

  # ===================================================
  # ################ Database Settings ################
  # ===================================================
  # Shared DB config vars
  DB_TYPE: str = "postgres"  # postgres, mysql, or sqlite
  DB_USERNAME: str = "postgres"
  DB_PASSWORD: str = "password"
  DB_HOST: str = "localhost"
  DB_PORT: int = 5432
  DB_NAME: str = "postgres"
  SQLITE_BASE_DIR: str = './data/db'
  DB_SCHEME: str = "" # Will be set in constructor
  DB_DRIVER: str = "" # Will be set in constructor

  # Constructed Database URL - async drivers only
  DATABASE_URL: str = ""  # Will be set in constructor
  DATABASE_URL_SYNC: str = ""  # Will be set in constructor
  
  # Database debugging (used in async mode)
  SQL_ECHO: bool = False
  
  # Async connection settings
  DATABASE_POOL_RECYCLE: int = 3600  # Connection recycling interval

  # Dagster Configuration
  DAGSTER_DB_NAME: str = "system_dagster"


  # ===================================================
  # ############## Settings Initialization ############
  # ===================================================
  def __init__(self, **values):
    """Initialize settings with async driver based on DB_TYPE."""
    super().__init__(**values)
    self.configure_database_connections(self.DB_TYPE)
    self.configure_dagster()

  def configure_database_connections(self, database_type: str) -> None:
    match (database_type):
      case "postgres":
        self.DB_SCHEME = "postgresql"
        self.DB_DRIVER = "asyncpg"
      case "mysql":
        self.DB_SCHEME = "mysql"
        self.DB_DRIVER = "aiomysql"
      case "sqlite":
        self.DB_SCHEME = "sqlite"
        self.DB_DRIVER = "aiosqlite"
      case _:
          raise ValueError(f"Unsupported database type: {database_type}")
    """Configure the base database URL."""
    self.DATABASE_URL = f"{self.DB_SCHEME}+{self.DB_DRIVER}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    self.DATABASE_URL_SYNC = f"{self.DB_SCHEME}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    self.DAGSTER_DATABASE_URL = f"{self.DB_SCHEME}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DAGSTER_DB_NAME}"

  def configure_dagster(self) -> None:
    """Generate the Dagster configuration file."""
    pass


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

  @property
  def is_production(self) -> bool:
    """Check if running in production environment."""
    return self.ENVIRONMENT.lower() == "production"


settings = Settings()

# Validate async configuration on import
settings.validate_async_database()
