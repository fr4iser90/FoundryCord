from typing import List
from datetime import datetime
from .base_repository import BaseRepository
from core.models.ip import IP  # Sie müssen dieses Model erstellen

class IPRepository(BaseRepository[IP]):
    async def get_by_address(self, address: str) -> IP:
        result = await self.session.execute(
            select(self.model).filter(self.model.address == address)
        )
        return result.scalar_one_or_none()

    async def get_active_ips(self) -> List[IP]:
        result = await self.session.execute(
            select(self.model)
            .filter(self.model.is_active == True)
            .order_by(self.model.last_seen.desc())
        )
        return result.scalars().all()