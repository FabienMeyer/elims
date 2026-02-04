"""Main API router for aggregating all module-specific routers."""

from app.api.instruments.routes import router_collection as router_collection_instruments
from app.api.instruments.routes import router_resource as router_resource_instruments
from app.api.locations.routes import router_collection as router_collection_locations
from app.api.locations.routes import router_resource as router_resource_locations
from app.api.temperature.routes import router_collection as router_collection_temperature
from app.api.temperature.routes import router_resource as router_resource_temperature
from fastapi import APIRouter

router = APIRouter()

router.include_router(router_collection_instruments)
router.include_router(router_resource_instruments)
router.include_router(router_collection_locations)
router.include_router(router_resource_locations)
router.include_router(router_collection_temperature)
router.include_router(router_resource_temperature)
