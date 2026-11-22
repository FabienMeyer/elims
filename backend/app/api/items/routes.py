"""Item HTTP adapter."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.items.schemas import ItemCreate, ItemRead
from app.api.items.services import ItemService
from app.db import get_session

router = APIRouter(prefix="/items", tags=["items"])


def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> ItemService:
    """Build the item service."""
    return ItemService(session)


@router.get("/", response_model=list[ItemRead])
async def list_items(
    service: Annotated[ItemService, Depends(get_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ItemRead]:
    """List items."""
    return await service.list(limit=limit, offset=offset)


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(payload: ItemCreate, service: Annotated[ItemService, Depends(get_service)]) -> ItemRead:
    """Create an item."""
    return await service.create(payload)
