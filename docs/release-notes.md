# Release Notes

## Latest Changes

### Features

- Initial release of ELIMS - Electronic Laboratory Instrument Management System

### Infrastructure

- Docker Compose setup with MariaDB, Redis, Mosquitto MQTT, and Grafana stack
- Observability with Loki, Alloy, and Grafana for logging and monitoring
- Traefik reverse proxy for HTTPS and routing

### Backend

- FastAPI backend with SQLModel ORM
- Python 3.13 with uv package manager
- Configured with mypy, ruff, and pytest

### Frontend

- React 19 with TypeScript and Vite
- Tailwind CSS for styling
- TanStack Query and Router for state and routing
- Playwright for E2E testing

## 0.0.1

Initial release
