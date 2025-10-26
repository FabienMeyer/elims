"""Main API router for aggregating all module-specific routers."""

from fastapi import APIRouter

from elims.api.modules.instruments.routes import router as instruments_router

router = APIRouter()

router.include_router(instruments_router)
