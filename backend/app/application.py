"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from elims_database import Database
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.items.routes import router as items_router
from app.api.system.routes import router as system_router
from app.config import Settings, get_settings
from app.logging import configure_logging, log_request
from app.security import require_application_access


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the ASGI application."""
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        database = Database(settings.database_url.get_secret_value())
        application.state.database = database
        try:
            yield
        finally:
            await database.dispose()

    configure_logging()
    app = FastAPI(title=settings.project_name, version="0.1.0", debug=settings.app_debug, lifespan=lifespan)
    app.state.settings = settings
    app.middleware("http")(log_request)
    # No route uses cookies or other browser credentials; enable allow_credentials only when one does.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(system_router)
    app.include_router(system_router, prefix="/api", include_in_schema=False)
    app.include_router(items_router, prefix="/api/v1", dependencies=[Depends(require_application_access)])
    Instrumentator(registry=CollectorRegistry(), excluded_handlers=["/metrics"]).instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False,
    )
    return app
