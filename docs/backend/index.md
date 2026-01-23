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

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── db.py                # Database connection and session
│   ├── logger.py            # Logging configuration
│   ├── routers.py           # Router registration
│   ├── py.typed             # Type checking marker
│   ├── alembic/             # Database migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/        # Migration files
│   ├── api/                 # API endpoints
│   │   └── __init__.py
│   └── core/                # Core business logic
│       └── __init__.py
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest configuration
│   ├── api/                 # API tests
│   └── core/                # Core logic tests
├── Dockerfile               # Multi-stage production build
├── pyproject.toml           # Project dependencies and config
├── alembic.ini              # Alembic configuration
└── README.md
```

## Architecture

### Application Layers

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
│  ┌─────────────────────────────┐   │
│  │   Routers & Endpoints       │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│        Business Logic Layer         │
│  ┌─────────────────────────────┐   │
│  │   Services & Core Logic     │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│         Data Access Layer           │
│  ┌─────────────────────────────┐   │
│  │   SQLModel Models & ORM     │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│            Database                 │
│         MariaDB + Redis             │
└─────────────────────────────────────┘
```

### Key Components

#### 1. Main Application (`main.py`)

Entry point for the FastAPI application:

```python
from fastapi import FastAPI
from app.config import settings
from app.logger import logger
from app.routers import setup_routers

app = FastAPI(
    title="ELIMS API",
    description="Electronic Laboratory Instrument Management System",
    version="0.0.1",
)

# Setup routers
setup_routers(app)

@app.on_event("startup")
async def startup():
    logger.info("Starting ELIMS Backend")
    # Initialize database, cache, etc.

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down ELIMS Backend")
    # Cleanup resources
```

#### 2. Configuration (`config.py`)

Manages application configuration using Pydantic Settings:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    MARIADB_HOST: str
    MARIADB_PORT: int = 3306
    MARIADB_USER: str
    MARIADB_PASSWORD: str
    MARIADB_DATABASE: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str

    # MQTT
    MQTT_HOST: str
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str
    MQTT_PASSWORD: str

    # Backend
    BACKEND_SECRET_KEY: str
    BACKEND_ALGORITHM: str = "HS256"
    BACKEND_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    BACKEND_CORS_ORIGINS: str

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
```

#### 3. Database (`db.py`)

Database connection and session management:

```python
from sqlmodel import Session, create_engine
from app.config import settings

# Database URL
DATABASE_URL = f"mysql+pymysql://{settings.MARIADB_USER}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_HOST}:{settings.MARIADB_PORT}/{settings.MARIADB_DATABASE}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
    pool_recycle=3600,
)

def get_session():
    with Session(engine) as session:
        yield session
```

#### 4. Logging (`logger.py`)

Centralized logging using Loguru:

```python
from loguru import logger
import sys

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

# Add file handler for production
if settings.ENVIRONMENT == "production":
    logger.add(
        "logs/elims.log",
        rotation="500 MB",
        retention="10 days",
        compression="zip",
    )
```

#### 5. Routers (`routers.py`)

Router registration and organization:

```python
from fastapi import FastAPI
from app.api import instruments, locations, users

def setup_routers(app: FastAPI):
    """Register all API routers"""
    app.include_router(
        instruments.router,
        prefix="/api/instruments",
        tags=["instruments"],
    )
    app.include_router(
        locations.router,
        prefix="/api/locations",
        tags=["locations"],
    )
    app.include_router(
        users.router,
        prefix="/api/users",
        tags=["users"],
    )
```

## Database Models

### Example: SQLModel Models

```python
from sqlmodel import Field, SQLModel
from datetime import datetime

class InstrumentBase(SQLModel):
    name: str
    model: str
    serial_number: str
    location_id: int
    status: str = "active"

class Instrument(InstrumentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InstrumentCreate(InstrumentBase):
    pass

class InstrumentRead(InstrumentBase):
    id: int
    created_at: datetime
    updated_at: datetime

class InstrumentUpdate(SQLModel):
    name: str | None = None
    model: str | None = None
    status: str | None = None
```

## API Endpoints

### Standard CRUD Pattern

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import Instrument, InstrumentCreate, InstrumentRead, InstrumentUpdate

router = APIRouter()

@router.get("/", response_model=list[InstrumentRead])
async def list_instruments(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """List all instruments"""
    statement = select(Instrument).offset(skip).limit(limit)
    instruments = session.exec(statement).all()
    return instruments

@router.get("/{instrument_id}", response_model=InstrumentRead)
async def get_instrument(
    instrument_id: int,
    session: Session = Depends(get_session),
):
    """Get instrument by ID"""
    instrument = session.get(Instrument, instrument_id)
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return instrument

@router.post("/", response_model=InstrumentRead)
async def create_instrument(
    instrument: InstrumentCreate,
    session: Session = Depends(get_session),
):
    """Create new instrument"""
    db_instrument = Instrument.model_validate(instrument)
    session.add(db_instrument)
    session.commit()
    session.refresh(db_instrument)
    return db_instrument

@router.patch("/{instrument_id}", response_model=InstrumentRead)
async def update_instrument(
    instrument_id: int,
    instrument: InstrumentUpdate,
    session: Session = Depends(get_session),
):
    """Update instrument"""
    db_instrument = session.get(Instrument, instrument_id)
    if not db_instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    update_data = instrument.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_instrument, key, value)

    session.add(db_instrument)
    session.commit()
    session.refresh(db_instrument)
    return db_instrument

@router.delete("/{instrument_id}")
async def delete_instrument(
    instrument_id: int,
    session: Session = Depends(get_session),
):
    """Delete instrument"""
    instrument = session.get(Instrument, instrument_id)
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    session.delete(instrument)
    session.commit()
    return {"ok": True}
```

## Database Migrations

### Using Alembic

#### Create Migration

```bash
# Auto-generate migration from models
uv run alembic revision --autogenerate -m "Add instruments table"

# Create empty migration
uv run alembic revision -m "Custom migration"
```

#### Apply Migrations

```bash
# Upgrade to latest
uv run alembic upgrade head

# Upgrade one version
uv run alembic upgrade +1

# Downgrade one version
uv run alembic downgrade -1

# Show current version
uv run alembic current

# Show history
uv run alembic history
```

#### Migration Example

```python
"""Add instruments table

Revision ID: 001
Revises:
Create Date: 2026-01-23
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'instrument',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('model', sa.String(length=255), nullable=False),
        sa.Column('serial_number', sa.String(length=255), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('instrument')
```

## Testing

### Test Structure

```python
# tests/conftest.py
import pytest
from sqlmodel import Session, create_engine, SQLModel
from app.main import app
from app.db import get_session

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
```

### Example Tests

```python
# tests/api/test_instruments.py
def test_create_instrument(client):
    response = client.post(
        "/api/instruments/",
        json={
            "name": "Test Instrument",
            "model": "TEST-100",
            "serial_number": "SN12345",
            "location_id": 1,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Instrument"
    assert "id" in data

def test_list_instruments(client):
    response = client.get("/api/instruments/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_instrument_not_found(client):
    response = client.get("/api/instruments/999")
    assert response.status_code == 404
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test
uv run pytest tests/api/test_instruments.py

# Run with verbose output
uv run pytest -v

# Run with print statements
uv run pytest -s
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/FabienMeyer/elims.git
cd elims/backend

# Install dependencies
uv sync

# Copy environment file
cp ../.env.example ../.env
# Edit .env with your configuration

# Run migrations
uv run alembic upgrade head

# Run development server
uv run fastapi dev app/main.py
```

### Code Quality

```bash
# Type checking
uv run mypy app

# Linting
uv run ruff check app

# Auto-fix linting issues
uv run ruff check app --fix

# Format code
uv run ruff format app

# Check formatting
uv run ruff format app --check
```

### Development Server

```bash
# FastAPI development server (auto-reload)
uv run fastapi dev app/main.py

# Uvicorn directly
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# With specific log level
uv run fastapi dev app/main.py --log-level debug
```

### API Documentation

FastAPI automatically generates API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Production Deployment

### Docker Build

The Dockerfile uses a multi-stage build:

1. **Base**: Python 3.13 with uv
1. **Dependencies**: Install dependencies
1. **Production**: Copy app and run with Gunicorn

```dockerfile
FROM python:3.13-slim as base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application
COPY . .

# Run with Gunicorn
CMD ["uv", "run", "gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Environment Variables

Required in production:

```env
# Database
MARIADB_HOST=mariadb
MARIADB_PORT=3306
MARIADB_USER=elims
MARIADB_PASSWORD=secure_password
MARIADB_DATABASE=elims

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=secure_password

# MQTT
MQTT_HOST=mosquitto
MQTT_PORT=1883
MQTT_USERNAME=elims
MQTT_PASSWORD=secure_password

# Backend
BACKEND_SECRET_KEY=generate_with_openssl_rand_hex_32
BACKEND_ALGORITHM=HS256
BACKEND_ACCESS_TOKEN_EXPIRE_MINUTES=60
BACKEND_CORS_ORIGINS=https://example.com
ENVIRONMENT=production
```

### Performance Tuning

```bash
# Gunicorn with multiple workers
gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

## Best Practices

### API Design

1. **Use Pydantic Models**: For request/response validation
1. **Depend on get_session**: For database access
1. **Use HTTP Status Codes**: Correctly (200, 201, 404, 422, etc.)
1. **Add Response Models**: For type safety and docs
1. **Include Docstrings**: For API documentation

### Database

1. **Use Transactions**: For data consistency
1. **Add Indexes**: For frequently queried fields
1. **Implement Soft Deletes**: For audit trails
1. **Use Connection Pooling**: For performance
1. **Regular Backups**: Automated and tested

### Security

1. **Input Validation**: Pydantic models + custom validators
1. **SQL Injection Protection**: Use ORM (SQLModel)
1. **Authentication**: JWT tokens
1. **Authorization**: Role-based access control
1. **HTTPS Only**: In production
1. **CORS Configuration**: Whitelist specific origins

### Error Handling

```python
from fastapi import HTTPException

# Client errors (4xx)
raise HTTPException(status_code=400, detail="Bad request")
raise HTTPException(status_code=404, detail="Not found")
raise HTTPException(status_code=422, detail="Validation error")

# Server errors (5xx)
raise HTTPException(status_code=500, detail="Internal server error")
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**

   - Check environment variables
   - Verify database is running
   - Test connection manually

1. **Import Errors**

   - Ensure dependencies are installed
   - Check Python path
   - Verify module structure

1. **Migration Issues**

   - Check database permissions
   - Verify Alembic configuration
   - Review migration history

### Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Enhanced logging
logger.debug(f"Processing instrument: {instrument}")
logger.info("Request completed")
logger.warning("Deprecated endpoint used")
logger.error("Database error", exc_info=True)
```

## Related Documentation

- [Frontend Documentation](../frontend/index.md)
- [Workflows Documentation](../workflows/index.md)
- [Package Documentation](../packages/elims-common/index.md)
