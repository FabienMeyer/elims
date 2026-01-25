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

# Install dependencies (without local packages first)
RUN uv pip install --system fastapi pydantic pydantic-settings 'uvicorn[standard]' pytest pytest-cov pytest-asyncio httpx ruff mypy

# Expose port
EXPOSE 8000

# Development command
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 3: Production
FROM base AS production

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY backend ./backend

# Install production dependencies only
RUN uv pip install --system fastapi pydantic pydantic-settings 'uvicorn[standard]'

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Production command with Gunicorn
CMD ["gunicorn", "backend.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
