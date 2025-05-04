from abc import ABC, abstractmethod
from typing import List, Optional
from app.shared.infrastructure.models.project.task_entity import Task

class TaskRepository(ABC):
    """Interface for task repository operations"""
    
    @abstractmethod
    async def create_task(self, task: Task) -> Optional[Task]:
        """Create a new task in the database"""
        pass
    
    @abstractmethod
    async def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        pass
    
    @abstractmethod
    async def get_tasks_by_project(self, project_id: int) -> List[Task]:
        """Get all tasks for a project"""
        pass
    
    @abstractmethod
    async def update_task(self, task_id: int, **updates) -> bool:
        """Update a task with the given fields"""
        pass
    
    @abstractmethod
    async def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID"""
        pass
    
    @abstractmethod
    async def assign_task(self, task_id: int, user_id: str) -> bool:
        """Assign a task to a user"""
        pass 