from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.infrastructure.database.models import Project, Task
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, project_id: int) -> Optional[Project]:
        result = await self.session.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Project]:
        result = await self.session.execute(select(Project).where(Project.name == name))
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Project]:
        result = await self.session.execute(select(Project))
        return result.scalars().all()
    
    async def create(self, name: str, description: str, status: str = "planning", 
                    priority: str = "medium", created_by: Optional[str] = None) -> Project:
        project = Project(
            name=name,
            description=description,
            status=status,
            priority=priority,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        self.session.add(project)
        await self.session.commit()
        return project
    
    async def update(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.commit()
        return project
    
    async def delete(self, project: Project) -> None:
        await self.session.delete(project)
        await self.session.commit()
