"""CLI smoke tests."""

import sys

import pytest
from typer.testing import CliRunner

from elims_cli.app import app, main


def test_help() -> None:
    """The command-line application starts and displays help."""
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "ELIMS command-line interface" in result.stdout


def test_console_script_entry_point_shows_help(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The console-script entry point runs the application with the process arguments."""
    monkeypatch.setattr(sys, "argv", ["elims", "--help"])

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 0
    assert "ELIMS command-line interface" in capsys.readouterr().out
