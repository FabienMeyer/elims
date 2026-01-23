# ELIMS - Lab Instrument Management System

[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://fabienmeyer.github.io/elims/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-passing-brightgreen.svg)](.github/workflows/)

## Core Services:

```
Frontend: [Vite/](https://vite.dev/)/[React](https://react.dev/) using [TanStack Query](https://tanstack.com/query/latest) and [Zustand/Redux](https://zustand.docs.pmnd.rs/middlewares/reduxDocker) , served via a multi-stage [Docker](https://www.docker.com/) build.

Backend: [FastAPI](https://fastapi.tiangolo.com/) using [sqlmodels](https://sqlmodel.tiangolo.com/) and [Uvicorn](https://uvicorn.dev/)/[Gunicorn](https://gunicorn.org/) behind [Nginx](https://nginx.org/) served via a multi-stage Docker build.

Database: [MariaDB](https://mariadb.org/) using [Adminer](https://www.adminer.org/) for management served via Docker.

Cache: [Redis](https://redis.io/) 7 (Alpine) for session and database caching.

Broker: [Mosquitto MQTT](https://mosquitto.org/) for real-time messaging serve via Docker and internal Docker network.
```

## Infrastructure & Security

```
Gateway: Nginx as a reverse proxy handling HTTP React, API (/api).

Authentication: Basic Auth on the Nginx level for sensitive routes using an .htpasswd file.

Secrets: All sensitive data is managed via a root .env file.
```

## Observability (The LGMA Stack)

```
[Alloy](https://grafana.com/docs/alloy/latest/): Acting as the collector, scraping Docker container logs via the socket.

[Loki](https://grafana.com/docs/loki/latest/): Centralized log storage with a health check at /ready.

[Grafana](https://grafana.com/docs/grafana/latest/): Visualization dashboard connected to Loki.
Loki-Canary: Running as a watchdog to ensure log ingestion integrity.
```

## Organization

```
Folder Structure: Config files are in ./config/, persistent data volumes are managed by Docker, and application code is in ./frontend/ and ./backend/.
```

## Python Backend/Package Setup

```
Package Management: using [uv](https://docs.astral.sh/uv/)
Virtual Environment: using [venv](https://docs.python.org/3/library/venv.html)
Linting & Formatting: using [ruff](https://docs.astral.sh/ruff/)
Type Checking: using [mypy](https://docs.astral.sh/mypy/)
Testing: using [pytest](https://docs.astral.sh/pytest/)
```

## Docker Compose

```
Orchestration: All services are orchestrated using [Docker Compose](https://docs.docker.com/compose/).

Network: Services communicate over an internal Docker network for security and isolation.

Configuration: All service configurations are managed via Docker Compose YAML files and environment variables. Configuration files are stored in the ./config/ directory.

All services need to be ready for production use, with proper error handling, logging, and security measures in place.
```

## Documentation

Full documentation is available at: [https://fabienmeyer.github.io/elims/](https://fabienmeyer.github.io/elims/)

- **Latest** (development): [https://fabienmeyer.github.io/elims/latest/](https://fabienmeyer.github.io/elims/latest/)
- **Stable** (latest release): [https://fabienmeyer.github.io/elims/stable/](https://fabienmeyer.github.io/elims/stable/)

### Build Documentation Locally

```bash
# Install dependencies
uv tool install mkdocs-material mike

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

Visit: http://localhost:8000
