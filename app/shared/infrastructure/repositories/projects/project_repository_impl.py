from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.models import ProjectEntity, Task
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProjectRepositoryImpl(BaseRepositoryImpl[ProjectEntity]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProjectEntity, session)
    
    async def get_by_id(self, project_id: int) -> Optional[ProjectEntity]:
        result = await self.session.execute(select(self.model).where(self.model.id == project_id))
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[ProjectEntity]:
        result = await self.session.execute(select(self.model).where(self.model.name == name))
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[ProjectEntity]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()
    
    async def get_projects_by_guild(self, guild_id: str) -> List[ProjectEntity]:
        """Fetch projects associated with a specific guild ID."""
        stmt = select(self.model).where(self.model.guild_id == str(guild_id))
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, name: str, description: str, status: str = "planning", 
                    priority: str = "medium", created_by: Optional[str] = None) -> ProjectEntity:
        project = ProjectEntity(
            name=name,
            description=description,
            status=status,
            priority=priority,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        self.session.add(project)
        await self.session.flush()
        await self.session.refresh(project)
        return project
    
    async def update(self, project: ProjectEntity) -> ProjectEntity:
        self.session.add(project)
        await self.session.flush()
        await self.session.refresh(project)
        return project
    
    async def delete(self, project: ProjectEntity) -> None:
        await super().delete(project)
