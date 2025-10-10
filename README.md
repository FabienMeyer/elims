# elims

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/elims)
![CI](https://github.com/FabienMeyer/e-lims-d2xx/actions/workflows/ci.yml/badge.svg)
[![Codecov](https://codecov.io/gh/FabienMeyer/e-lims-d2xx/graph/badge.svg?token=xp3TKuNLKh)](https://codecov.io/gh/FabienMeyer/elims)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=FabienMeyer_elims&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=FabienMeyer_elims)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=FabienMeyer_elims&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=FabienMeyer_elims)
![PyPI](https://img.shields.io/pypi/v/elims.svg)
[![Documentation](https://img.shields.io/badge/GitHub-Pages-blue)](https://fabienmeyer.github.io/elims/)
![License](https://img.shields.io/github/license/FabienMeyer/elims)

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
