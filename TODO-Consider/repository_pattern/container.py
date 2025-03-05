from typing import List
from .base_repository import BaseRepository
from core.models.container import Container  # Sie müssen dieses Model erstellen

class ContainerRepository(BaseRepository[Container]):
    async def get_running_containers(self) -> List[Container]:
        result = await self.session.execute(
            select(self.model).filter(self.model.status == "running")
        )
        return result.scalars().all()

    async def get_by_name(self, name: str) -> Container:
        result = await self.session.execute(
            select(self.model).filter(self.model.name == name)
        )
        return result.scalar_one_or_none()