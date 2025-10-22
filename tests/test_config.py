"""Tests for the configuration settings of the application."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from elims.config import AppEnvironment, Settings


class TestAppEnvironment:
    """Tests for the AppEnvironment enum and Settings integration."""

    def test_app_env_default_value(self) -> None:
        """Test that AppEnvironment defaults to DEVELOPMENT when not set."""
        settings = Settings()
        assert settings.app_env == AppEnvironment.DEVELOPMENT

    @pytest.mark.parametrize(
        ("env_value", "expected_value"),
        [
            ("development", AppEnvironment.DEVELOPMENT),
            ("test", AppEnvironment.TEST),
            ("production", AppEnvironment.PRODUCTION),
        ],
    )
    def test_app_env_from_env_variable(self, monkeypatch: pytest.MonkeyPatch, *, env_value: str, expected_value: AppEnvironment) -> None:
        """Test AppEnvironment setting from environment variable."""
        monkeypatch.setenv("APP_ENV", env_value)
        settings = Settings()
        assert settings.app_env == expected_value

    def test_sql_echo_default_value(self) -> None:
        """Test that SQL_ECHO defaults to False when not set."""
        settings = Settings()
        assert settings.sql_echo is False

    @pytest.mark.parametrize(
        ("env_value", "expected_value"),
        [
            ("True", True),
            ("False", False),
        ],
    )
    def test_sql_echo_from_env_variable(self, monkeypatch: pytest.MonkeyPatch, *, env_value: str, expected_value: bool) -> None:
        """Test SQL_ECHO setting from environment variable."""
        monkeypatch.setenv("SQL_ECHO", env_value)
        settings = Settings()
        assert settings.sql_echo is expected_value

    def test_sqlite_path_default_value(self) -> None:
        """Test that SQLITE_PATH defaults to 'app.db' when not set."""
        settings = Settings()
        assert settings.sqlite_path == Path("app.db")

    @pytest.mark.parametrize(
        ("env_value", "expected_value"),
        [
            ("data/custom.db", Path("data/custom.db")),
        ],
    )
    def test_sqlite_path_from_env_variable(self, monkeypatch: pytest.MonkeyPatch, env_value: str, expected_value: Path) -> None:
        """Test SQLITE_PATH setting from environment variable."""
        monkeypatch.setenv("SQLITE_PATH", env_value)
        settings = Settings()
        assert settings.sqlite_path == expected_value

    def test_sqlite_check_same_thread_default_value(self) -> None:
        """Test that SQLITE_CHECK_SAME_THREAD defaults to False when not set."""
        settings = Settings()
        assert settings.sqlite_check_same_thread is False

    @pytest.mark.parametrize(
        ("env_value", "expected_value"),
        [
            ("True", True),
            ("False", False),
        ],
    )
    def test_sqlite_check_same_thread_from_env_variable(self, monkeypatch: pytest.MonkeyPatch, *, env_value: str, expected_value: bool) -> None:
        """Test SQLITE_CHECK_SAME_THREAD setting from environment variable."""
        monkeypatch.setenv("SQLITE_CHECK_SAME_THREAD", env_value)
        settings = Settings()
        assert settings.sqlite_check_same_thread is expected_value

    @pytest.mark.parametrize(
        ("sqlite_path", "expected_url"),
        [
            (Path("app.db"), "sqlite:///app.db"),
            (Path("data/custom.db"), "sqlite:///data/custom.db"),
            (Path(":memory:"), "sqlite:///:memory:"),
        ],
    )
    def test_db_url(self, monkeypatch: pytest.MonkeyPatch, sqlite_path: Path, expected_url: str) -> None:
        """Test that db_url returns correct SQLite URL."""
        monkeypatch.setenv("SQLITE_PATH", str(sqlite_path))
        settings = Settings()
        assert settings.db_url == expected_url

    def test_db_url_invalid_architecture(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Unsupported DB_ARCHITECTURE is rejected during settings validation."""
        monkeypatch.setenv("DB_ARCHITECTURE", "unsupported_arch")
        with pytest.raises(ValidationError, match="Input should be 'sqlite'"):
            _ = Settings()
