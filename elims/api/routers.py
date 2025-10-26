"""Main API router for aggregating all module-specific routers."""

from fastapi import APIRouter

from elims.api.modules.instruments.routes import router_collection, router_resource

router = APIRouter()

router.include_router(router_collection)
router.include_router(router_resource)
