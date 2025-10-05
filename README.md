# elims

## Pre-commit

### Install hooks (already done)

uv run pre-commit install

### Run on all files

uv run pre-commit run --all-files

### Run on specific files

uv run pre-commit run --files path/to/file.py

### Update hook versions

uv run pre-commit auto update

## Bandit

uv run ruff check elims/ # Uses [tool.ruff]
uv run mypy elims/ # Uses [tool.mypy]
uv run mdformat docs/ # Uses [tool.mdformat]
uv run vale
uv run pre-commit run --all-files # Uses pyproject.toml configs
