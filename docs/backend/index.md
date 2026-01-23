# Backend Documentation

## Overview

The ELIMS backend is a FastAPI-based REST API that provides the core functionality for the laboratory instrument management system. It handles data persistence, business logic, and provides a modern, async API for the frontend application.

## Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) 0.128+
- **Python**: 3.13+
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) (combines SQLAlchemy + Pydantic)
- **Database**: MariaDB 11
- **Cache**: Redis 7
- **Message Broker**: Mosquitto MQTT
- **Server**: Uvicorn with Gunicorn
- **Migrations**: Alembic
- **Logging**: Loguru
