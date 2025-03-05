from typing import Optional, List
from .base_repository import BaseRepository
from core.models.user import User  # Sie müssen dieses Model erstellen

class UserRepository(BaseRepository[User]):
    async def get_by_discord_id(self, discord_id: str) -> Optional[User]:
        result = await self.session.execute(
            select(self.model).filter(self.model.discord_id == discord_id)
        )
        return result.scalar_one_or_none()

    async def get_active_users(self) -> List[User]:
        result = await self.session.execute(
            select(self.model).filter(self.model.is_active == True)
        )
        return result.scalars().all()