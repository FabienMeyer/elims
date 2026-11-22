# Full-stack Project Template

Minimal template with FastAPI, SQLModel, MariaDB, React/TypeScript, TanStack Query, Nginx, Traefik, Docker, Prometheus, Grafana, Pytest, Vitest, Playwright, Ruff, Mypy, and MkDocs.

The workspace also includes `elims-cli`, `elims-utils`, `elims-com`, `elims-database`, and `elims-instruments` as reusable Python package examples.

CLI shell:

```bash
uv tool install ./packages/elims-cli
elims --help
```

```powershell
Copy-Item .env.example .env
docker compose --profile observability up --build
```

- Frontend: <http://localhost:8080>
- Backend: <http://localhost:8000>
- OpenAPI: <http://localhost:8000/docs>
- Grafana: <http://localhost:3000>
- Prometheus: <http://localhost:9090>

See [docs/architecture.md](./docs/architecture.md) for the template boundaries.

See the [command reference](./docs/operations/command-reference.md) for setup, development, testing, documentation, Docker, security, and release commands.
