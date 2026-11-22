# Python packages

The workspace contains small Python packages with explicit boundaries and public APIs. Each package uses a `src/` layout and can be built and released independently.

| Package | Purpose | Import namespace |
| --- | --- | --- |
| `elims-cli` | Minimal Typer application shell | `elims_cli` |
| `elims-utils` | Framework-independent utility functions | `elims_utils` |
| `elims-com` | Transport-neutral communication contracts | `elims_com` |
| `elims-database` | Asynchronous SQLModel database infrastructure | `elims_database` |
| `elims-instruments` | Instrument-domain models | `elims_instruments` |

## Development

Install every workspace package and the development tools:

```bash
uv sync --all-packages --all-extras --group dev
```

Run the shared quality checks:

```bash
uv run ruff check packages
uv run ruff format --check packages
uv run mypy packages/elims-cli/src packages/elims-utils/src packages/elims-com/src packages/elims-database/src packages/elims-instruments/src
uv run pytest packages
```

Each package also includes an independent `mkdocs.yml`. From a package directory, build or serve its documentation with:

```bash
uv sync --extra docs
uv run mkdocs build --strict
uv run mkdocs serve
```
