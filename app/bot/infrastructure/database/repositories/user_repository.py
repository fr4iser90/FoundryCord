from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.models import User
from typing import Optional, List

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_discord_id(self, discord_id: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.discord_id == discord_id))
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()
    
    async def create(self, discord_id: str, username: str, role: str) -> User:
        user = User(discord_id=discord_id, username=username, role=role)
        self.session.add(user)
        await self.session.commit()
        return user
    
    async def update(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        return user
    
    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()
