"""Configuration settings for the Glass Box Portfolio backend."""

import os
from functools import lru_cache

from pydantic import Field
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
    posthog_api_key: str = ""
    posthog_host: str = "https://eu.i.posthog.com"

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
    model_name: str = "google-gla:gemini-3-flash-preview"

    # Codebase Oracle Settings
    codebase_root: str = Field(default_factory=os.getcwd)
    max_file_lines: int = 500


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
