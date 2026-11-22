# Packages

Packages use a `src/` layout, publish an explicit API from `__init__.py`, and remain independent from application frameworks.

- `elims-cli` provides a minimal Typer application shell for future commands.
- `elims-utils` contains generic, framework-independent helpers.
- `elims-com` defines transport-neutral communication contracts.
- `elims-database` provides the async engine and SQLModel sessions.
- `elims-instruments` owns the instrument domain.
