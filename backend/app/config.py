"""Typed application configuration."""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def split_origins(value: str) -> list[str]:
    """Split a comma-separated origin list, dropping blanks."""
    return [origin.strip() for origin in value.split(",") if origin.strip()]


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    # Required: a deployment that forgets ENVIRONMENT must not start with development's open business routes.
    environment: Literal["development", "test", "production"]
    database_url: str = "sqlite+aiosqlite:///./app.db"
    backend_cors_origins: str = "http://localhost:5173"
    project_name: str = "Full-stack template"
    app_debug: bool = False

    @field_validator("backend_cors_origins")
    @classmethod
    def reject_wildcard_origins(cls, value: str) -> str:
        """Require explicit origins; '*' would let any website call the API from a user's browser."""
        if "*" in split_origins(value):
            raise ValueError("BACKEND_CORS_ORIGINS must list explicit origins, not '*'")
        return value

    @model_validator(mode="after")
    def validate_production(self) -> "Settings":
        """Reject development defaults when production is selected."""
        if self.environment == "production" and (
            self.app_debug or self.database_url.startswith("sqlite") or "change-me" in self.database_url
        ):
            raise ValueError("Production requires a configured database and debug disabled")
        return self

    # Validation errors would otherwise echo every input, including the database URL and its password.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)

    @property
    def cors_origins(self) -> list[str]:
        """Return normalized allowed origins."""
        return split_origins(self.backend_cors_origins)


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance."""
    return Settings()
