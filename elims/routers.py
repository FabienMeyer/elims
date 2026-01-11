"""Main API router for aggregating all module-specific routers."""

from fastapi import APIRouter

from elims.modules.instruments.routes import router_collection as router_collection_instruments
from elims.modules.instruments.routes import router_resource as router_resource_instruments
from elims.modules.locations.routes import router_collection as router_collection_locations
from elims.modules.locations.routes import router_resource as router_resource_locations

router = APIRouter()

router.include_router(router_collection_instruments)
router.include_router(router_resource_instruments)
router.include_router(router_collection_locations)
router.include_router(router_resource_locations)
