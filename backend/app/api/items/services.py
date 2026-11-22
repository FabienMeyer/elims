"""Item use cases."""

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.items.models import Item
from app.api.items.schemas import ItemCreate, ItemRead


class ItemService:
    """Coordinate item persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[ItemRead]:
        """List a bounded, stable page of items."""
        result = await self.session.exec(select(Item).order_by(col(Item.id)).offset(offset).limit(limit))
        return [ItemRead.model_validate(item) for item in result.all()]

    async def create(self, payload: ItemCreate) -> ItemRead:
        """Create one item."""
        item = Item.model_validate(payload)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return ItemRead.model_validate(item)
