# Backend development

From the repository root:

```bash
uv sync --locked --all-packages --all-extras --group dev
uv run ruff check backend packages
uv run ruff format --check backend packages
uv run mypy backend/app
uv run pytest backend/tests
```

Run the backend documentation independently from `backend/` with `uv run mkdocs build --strict`.
