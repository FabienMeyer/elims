"""ELIMS command-line application."""

import typer

app = typer.Typer(help="ELIMS command-line interface.")


@app.callback()
def cli() -> None:
    """Provide the root command group for future ELIMS commands."""


def main() -> None:
    """Console-script entry point."""
    app()


if __name__ == "__main__":
    main()
