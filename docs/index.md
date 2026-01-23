# ELIMS - Lab Instrument Management System

Welcome to the ELIMS documentation! ELIMS is a modern laboratory information management system designed to streamline instrument management, data collection, and laboratory workflows.

## Quick Start

Get started with ELIMS by exploring the documentation:

- **[API Documentation](api.md)** - Learn about the backend API endpoints and database models
- **[Contributing](contributing.md)** - Guidelines for contributing to the project
- **[Code of Conduct](code_of_conduct.md)** - Community standards and expectations

## Features

- **Real-time Monitoring**: Track laboratory instruments and data in real-time using MQTT
- **Modern Architecture**: Built with FastAPI (backend) and React (frontend)
- **Scalable Infrastructure**: Docker-based deployment with observability stack (Loki, Grafana, Alloy)
- **Secure**: Authentication, secure communication, and proper data handling

## Technology Stack

### Backend

- FastAPI with SQLModel
- MariaDB database
- Redis for caching
- MQTT (Mosquitto) for messaging

### Frontend

- React with TanStack Router and Query
- Vite for fast development
- Modern UI components

### Infrastructure

- Docker Compose orchestration
- Traefik reverse proxy with automatic SSL
- LGMA observability stack (Loki, Grafana, Alloy)

## Getting Started

Check out our [GitHub repository](https://github.com/FabienMeyer/elims) to get started with ELIMS.

## License

ELIMS is licensed under the [MIT License](license.md).
