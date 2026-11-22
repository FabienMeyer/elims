# ELIMS architecture

```text
Browser ──HTTP──> frontend ──HTTP──> backend ──SQL──> MariaDB
                                         └──> elims-database and domain packages
Traefik ──> frontend and backend
Prometheus ──> backend metrics ──> Grafana dashboards
MkDocs ──> aggregate and standalone package documentation
```

The repository separates deployable applications from reusable packages:

- `frontend/` contains the React and TypeScript application served by Nginx.
- `backend/` contains the FastAPI application and Alembic migrations.
- `packages/` contains independently buildable Python packages.
- `docs/` contains the aggregate project documentation.
- `config/` contains version-controlled infrastructure configuration for Grafana and Prometheus.

The `uv` workspace manages the backend and Python packages, while npm manages the frontend. Docker provides reproducible local and production environments. GitHub Actions validates formatting, typing, tests, builds, security, container images, and documentation.

The backend, frontend, and each Python package own standalone documentation. The root MkDocs build aggregates those canonical sources through `docs/hooks.py` without copying them into `docs/`.
