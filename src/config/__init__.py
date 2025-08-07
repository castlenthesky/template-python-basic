"""Application configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
  TEST: str = "UNCONFIGURED"

  class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"
    extra = "allow"


settings = Settings()
