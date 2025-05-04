import logging
from typing import List, Optional
from app.shared.infrastructure.database.service import DatabaseService
from app.shared.infrastructure.repositories.projects.task_repository_impl import TaskRepositoryImpl
from app.shared.infrastructure.models.project.task_entity import Task

logger = logging.getLogger("homelab.bot")

class TaskService:
    """Service for managing tasks within projects"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.task_repository = TaskRepositoryImpl(db_service)
    
    async def create_task(self, project_id: int, title: str, description: str = None, 
                         priority: str = None, assigned_to: str = None, 
                         due_date = None) -> Optional[Task]:
        """Create a new task for a project"""
        try:
            task = Task(
                project_id=project_id,
                title=title,
                description=description,
                priority=priority,
                assigned_to=assigned_to,
                due_date=due_date,
                status="todo"
            )
            
            return await self.task_repository.create_task(task)
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    async def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        try:
            return await self.task_repository.get_task(task_id)
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {e}")
            return None
    
    async def get_tasks_by_project(self, project_id: int) -> List[Task]:
        """Get all tasks for a project"""
        try:
            return await self.task_repository.get_tasks_by_project(project_id)
        except Exception as e:
            logger.error(f"Error getting tasks for project {project_id}: {e}")
            return []
    
    async def update_task(self, task_id: int, **updates) -> bool:
        """Update task details"""
        try:
            return await self.task_repository.update_task(task_id, **updates)
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return False
    
    async def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        try:
            return await self.task_repository.delete_task(task_id)
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return False
    
    async def assign_task(self, task_id: int, user_id: str) -> bool:
        """Assign a task to a user"""
        try:
            return await self.task_repository.assign_task(task_id, user_id)
        except Exception as e:
            logger.error(f"Error assigning task {task_id} to user {user_id}: {e}")
            return False
    
    async def change_status(self, task_id: int, new_status: str) -> bool:
        """Change the status of a task"""
        try:
            return await self.task_repository.update_task(task_id, status=new_status)
        except Exception as e:
            logger.error(f"Error changing status of task {task_id} to {new_status}: {e}")
            return False 