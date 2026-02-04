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
    MARIADB = "mariadb"


class Settings(BaseSettings):
    """Typed application settings."""

    environment: AppEnvironment = Field(default=AppEnvironment.DEVELOPMENT, description="Current environment")
    sql_echo: bool = Field(default=False, description="Enable SQL echo")

    db_architecture: DbArchitecture = Field(default=DbArchitecture.MARIADB, description="Database architecture")

    sqlite_path: Path = Field(default=Path("app.db"), description="SQLite file path or ':memory:'")
    sqlite_check_same_thread: bool = Field(default=False, description="SQLite check same thread flag")

    mariadb_host: str = Field(default="mariadb", description="MariaDB host")
    mariadb_port: int = Field(default=3306, description="MariaDB port")
    mariadb_user: str = Field(default="elims_user", description="MariaDB user")
    mariadb_password: str = Field(default="T6RdJWA4foCMEYzpxIhVa8PjsDXk9cHg", description="MariaDB password")
    mariadb_database: str = Field(default="elims", description="MariaDB database name")
    mariadb_root_password: str = Field(default="2Fj0nKzaRcT4EVBkDpLvifAyhUto5Cd1", description="MariaDB root password")

    # Redis Configuration
    redis_host: str = Field(default="redis", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_password: str = Field(default="mQ9wX3vN7bC2eR6fT0kL5pJ8hG4dA1sZ", description="Redis password")

    # Backend Configuration
    backend_secret_key: str = Field(
        default="yU8iO2pA5sD9fG1hJ4kL7zX0cV3bN6mQ9wE2rT5yU8iO2pA5sD9fG1hJ4kL7zX0c",
        description="Secret key for JWT",
    )
    backend_algorithm: str = Field(default="HS256", description="JWT algorithm")
    backend_access_token_expire_minutes: int = Field(default=30, description="Access token expiration time in minutes")
    backend_cors_origins: str = Field(default="http://localhost:3000,http://localhost:8080", description="Allowed CORS origins")

    # MQTT Configuration
    mqtt_host: str = Field(default="mosquitto", description="MQTT broker host")
    mqtt_port: int = Field(default=1883, description="MQTT broker port")
    mqtt_username: str = Field(default="elims_subscriber", description="MQTT username")
    mqtt_password: str = Field(default="mqtt_secure_password_123", description="MQTT password")
    mqtt_certificate_authority_file: Path = Field(default=Path("config/mosquitto/certs/ca.crt"), description="Path to MQTT CA certificate file")
    mqtt_certificate_file: Path = Field(default=Path("config/mosquitto/certs/client.crt"), description="Path to MQTT client certificate file")
    mqtt_key_file: Path = Field(default=Path("config/mosquitto/certs/client.key"), description="Path to MQTT client key file")

    # Project Configuration
    project_name: str = Field(default="ELIMS", description="Project name")
    stack_name: str = Field(default="elims", description="Stack name")
    domain: str = Field(default="localhost", description="Domain")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def db_url(self) -> str:
        """Construct the database URL from the settings."""
        match self.db_architecture:
            case DbArchitecture.SQLITE:
                path = ":memory:" if str(self.sqlite_path) == ":memory:" else self.sqlite_path.as_posix()
                return f"sqlite:///{path}"
            case DbArchitecture.MARIADB:
                return f"mysql://{self.mariadb_user}:{self.mariadb_password}@{self.mariadb_host}:{self.mariadb_port}/{self.mariadb_database}"


# Create a single instance of your settings
settings = Settings()
