from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database.models import Task
from typing import Optional, List
from datetime import datetime

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, task_id: int) -> Optional[Task]:
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()
    
    async def get_by_project_id(self, project_id: int) -> List[Task]:
        result = await self.session.execute(select(Task).where(Task.project_id == project_id))
        return result.scalars().all()
        
    async def get_by_status(self, status: str, project_id: Optional[int] = None) -> List[Task]:
        query = select(Task).where(Task.status == status)
        if project_id:
            query = query.where(Task.project_id == project_id)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create(self, project_id: int, title: str, description: str, 
                    priority: str, created_by: str) -> Task:
        task = Task(
            project_id=project_id,
            title=title,
            description=description or "",
            priority=priority,
            created_by=created_by
        )
        self.session.add(task)
        await self.session.commit()
        return task
    
    async def update_status(self, task_id: int, completed: bool) -> Optional[Task]:
        task = await self.get_by_id(task_id)
        if task:
            task.status = "completed" if completed else "open"
            if completed:
                task.completed_at = datetime.utcnow()
            else:
                task.completed_at = None
            self.session.add(task)
            await self.session.commit()
            return task
        return None
    
    async def update(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.commit()
        return task
    
    async def delete(self, task: Task) -> None:
        await self.session.delete(task)
        await self.session.commit()
