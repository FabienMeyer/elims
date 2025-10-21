"""Application configuration settings."""

from enum import Enum
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(Enum):
    """Application environment options."""

    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class DbArchitecture(Enum):
    """Database architecture options."""

    SQLITE = "sqlite"


class Settings(BaseSettings):
    """Typed application settings."""

    app_env: AppEnvironment = Field(default=AppEnvironment.DEVELOPMENT, description="Current environment")
    sql_echo: bool = Field(default=False, description="Enable SQL echo")

    db_architecture: DbArchitecture = Field(default=DbArchitecture.SQLITE, description="Database architecture")

    sqlite_path: Path = Field(default=Path("app.db"), description="SQLite file path or ':memory:'")
    sqlite_check_same_thread: bool = Field(default=False, description="SQLite check same thread flag")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def db_url(self) -> str:
        """Construct the database URL from the settings."""
        match self.db_architecture:
            case DbArchitecture.SQLITE:
                path = ":memory:" if str(self.sqlite_path) == ":memory:" else self.sqlite_path.as_posix()
                return f"sqlite:///{path}"
            case _:
                msg = "Unsupported database architecture"
                raise ValueError(msg)


# Create a single instance of your settings
settings = Settings()
