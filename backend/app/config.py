"""Typed application configuration."""

from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite+aiosqlite:///./app.db"
    backend_cors_origins: str = "http://localhost:5173"
    project_name: str = "Full-stack template"
    app_debug: bool = False

    @model_validator(mode="after")
    def validate_production(self) -> "Settings":
        """Reject development defaults when production is selected."""
        if self.environment == "production" and (
            self.app_debug or self.database_url.startswith("sqlite") or "change-me" in self.database_url
        ):
            raise ValueError("Production requires a configured database and debug disabled")
        return self

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        """Return normalized allowed origins."""
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance."""
    return Settings()
