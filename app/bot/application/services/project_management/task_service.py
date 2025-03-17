import logging
from typing import List, Optional, Dict
from datetime import datetime
import discord
from app.shared.infrastructure.database.service import DatabaseService
from app.shared.infrastructure.database.repositories.task_repository_impl import TaskRepository
from app.shared.infrastructure.database.models.project.task import Task

logger = logging.getLogger("homelab.bot")

class TaskService:
    """Service for managing tasks within projects"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.task_repository = TaskRepository(db_service)
    
    async def create_task(
        self, 
        project_id: int, 
        title: str, 
        description: str = None, 
        assignee_id: str = None,
        priority: int = 0,
        due_date = None
    ) -> Optional[Task]:
        """Create a new task in a project"""
        try:
            task = Task(
                project_id=project_id,
                title=title,
                description=description,
                assignee_id=assignee_id,
                status="todo",
                priority=priority,
                due_date=due_date
            )
            
            return await self.task_repository.create_task(task)
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    async def get_tasks_for_project(self, project_id: int) -> List[Task]:
        """Get all tasks for a project"""
        try:
            return await self.task_repository.get_tasks_by_project(project_id)
        except Exception as e:
            logger.error(f"Error getting tasks for project {project_id}: {e}")
            return []
    
    async def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        try:
            return await self.task_repository.get_task(task_id)
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {e}")
            return None
    
    async def update_task(self, task_id: int, **updates) -> bool:
        """Update a task"""
        try:
            return await self.task_repository.update_task(task_id, **updates)
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return False
    
    async def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        try:
            now = datetime.now()
            return await self.task_repository.update_task(
                task_id, 
                status="completed", 
                completed_at=now
            )
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {e}")
            return False
    
    async def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        try:
            return await self.task_repository.delete_task(task_id)
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return False 