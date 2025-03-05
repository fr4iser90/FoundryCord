from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy import select, delete, update

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> Optional[T]:
        result = await self.session.execute(
            select(self.model).filter(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[T]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        return instance

    async def update(self, id: int, **kwargs) -> Optional[T]:
        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0