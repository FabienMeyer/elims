"""Main API router for aggregating all module-specific routers."""

from fastapi import APIRouter

from elims.api.modules.authenticator.routes import router_collection as authentication_router_collection
from elims.api.modules.authenticator.routes import router_resource as authentication_router_resource
from elims.api.modules.instruments.routes import router_collection as instruments_router_collection
from elims.api.modules.instruments.routes import router_resource as instruments_router_resource
from elims.api.modules.locations.routes import router_collection as locations_router_collection
from elims.api.modules.locations.routes import router_resource as locations_router_resource
from elims.api.modules.users.routes import router_collection as users_router_collection
from elims.api.modules.users.routes import router_resource as users_router_resource

router = APIRouter()

router.include_router(authentication_router_collection)
router.include_router(authentication_router_resource)
router.include_router(instruments_router_collection)
router.include_router(instruments_router_resource)
router.include_router(locations_router_collection)
router.include_router(locations_router_resource)
router.include_router(users_router_collection)
router.include_router(users_router_resource)
