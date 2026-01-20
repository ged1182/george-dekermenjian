"""Configuration settings for the Glass Box Portfolio backend."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Keys
    gemini_api_key: str = ""

    # Application Settings
    app_name: str = "Glass Box Portfolio"
    app_version: str = "0.1.0"
    debug: bool = False

    # CORS Settings
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "https://*.vercel.app",
    ]

    # Model Settings
    model_name: str = "google-gla:gemini-2.0-flash"

    # Codebase Oracle Settings
    codebase_root: str = "/home/george-dekermenjian/git/george-dekermenjian"
    max_file_lines: int = 500


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
