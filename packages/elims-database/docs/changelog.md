# Changelog

Notable compatibility, migration, and operational changes are recorded here. Git history remains the source for low-level implementation changes.

## Unreleased

- Wheels and source distributions include the MIT license text.
- The `dev` and `docs` extras are no longer published. Development tools are uv dependency groups: use `uv sync --group dev` or `uv sync --group docs` instead of `--extra`.
- The minimum `sqlmodel` version is raised to 0.0.50, the version the workspace lockfile tests.
