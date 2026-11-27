# Changelog

Notable compatibility, migration, and operational changes are recorded here. Git history remains the source for low-level implementation changes.

## Unreleased

- Wheels and source distributions include the MIT license text.
- The `dev` and `docs` extras are no longer published. Development tools are uv dependency groups: use `uv sync --group dev` or `uv sync --group docs` instead of `--extra`.
- The `elims` console script calls `elims_cli.app:main`. Command behavior is unchanged.
