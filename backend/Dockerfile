# Multi-stage build for production

# Stage 1: Base Python image
FROM python:3.14-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Stage 2: Development
FROM base AS development

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY backend ./backend
COPY packages ./packages
COPY config ./backend/config

# Install local packages first (elims_common, elims_raspberry)
RUN uv pip install --system ./packages/elims-common

# Install all dependencies from pyproject.toml using uv pip
RUN uv pip install --system aiomysql alembic 'fastapi[standard]' loguru pydantic pydantic-settings pymysql sqlmodel 'uvicorn[standard]' pytest pytest-cov pytest-asyncio httpx ruff mypy

# Set working directory for development
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Development command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 3: Production
FROM base AS production

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY backend ./backend
COPY packages ./packages
COPY config ./backend/config

# Install local packages first (elims_common)
RUN uv pip install --system ./packages/elims-common

# Install production dependencies only
RUN uv pip install --system aiomysql alembic 'fastapi[standard]' loguru pydantic pydantic-settings pymysql sqlmodel 'uvicorn[standard]' gunicorn

# Set working directory for production
WORKDIR /app/backend

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Production command with Gunicorn
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
