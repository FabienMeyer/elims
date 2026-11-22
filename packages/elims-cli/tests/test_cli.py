"""CLI smoke tests."""

from typer.testing import CliRunner

from elims_cli.app import app


def test_help() -> None:
    """The command-line application starts and displays help."""
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "ELIMS command-line interface" in result.stdout
