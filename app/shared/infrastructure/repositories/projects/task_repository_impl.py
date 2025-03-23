from typing import List, Optional
from sqlalchemy import select, update, delete
from app.shared.domain.repositories.projects.task_repository import TaskRepository
from app.shared.infrastructure.database.service import DatabaseService
from app.shared.infrastructure.models.project.task import Task
import logging

logger = logging.getLogger("homelab.bot")

class TaskRepositoryImpl(TaskRepository):
    """Implementation of the task repository"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
    
    async def create_task(self, task: Task) -> Optional[Task]:
        """Create a new task"""
        try:
            async with self.db_service.session() as session:
                session.add(task)
                await session.commit()
                await session.refresh(task)
                return task
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    async def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        try:
            async with self.db_service.session() as session:
                result = await session.execute(
                    select(Task).where(Task.id == task_id)
                )
                return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}")
            return None
    
    async def get_tasks_by_project(self, project_id: int) -> List[Task]:
        """Get all tasks for a project"""
        try:
            async with self.db_service.session() as session:
                result = await session.execute(
                    select(Task).where(Task.project_id == project_id)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching tasks for project {project_id}: {e}")
            return []
    
    async def update_task(self, task_id: int, **updates) -> bool:
        """Update a task with the given fields"""
        try:
            async with self.db_service.session() as session:
                await session.execute(
                    update(Task)
                    .where(Task.id == task_id)
                    .values(**updates)
                )
                await session.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return False
    
    async def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID"""
        try:
            async with self.db_service.session() as session:
                await session.execute(
                    delete(Task).where(Task.id == task_id)
                )
                await session.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return False
    
    async def assign_task(self, task_id: int, user_id: str) -> bool:
        """Assign a task to a user"""
        try:
            async with self.db_service.session() as session:
                await session.execute(
                    update(Task)
                    .where(Task.id == task_id)
                    .values(assigned_to=user_id)
                )
                await session.commit()
                return True
        except Exception as e:
            logger.error(f"Error assigning task {task_id} to user {user_id}: {e}")
            return False
