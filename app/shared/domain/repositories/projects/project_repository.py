from abc import ABC, abstractmethod
from typing import List, Optional
from app.shared.infrastructure.models.project.project_entity import ProjectEntity

class ProjectRepository(ABC):
    """Interface for project repository operations"""
    
    @abstractmethod
    async def create_project(self, project: ProjectEntity) -> Optional[ProjectEntity]:
        """Create a new project in the database"""
        pass
    
    @abstractmethod
    async def get_project(self, project_id: int) -> Optional[ProjectEntity]:
        """Get a project by ID"""
        pass
    
    @abstractmethod
    async def get_projects_by_guild(self, guild_id: str) -> List[ProjectEntity]:
        """Get all projects for a guild"""
        pass
    
    @abstractmethod
    async def update_project(self, project_id: int, **updates) -> bool:
        """Update a project with the given fields"""
        pass
    
    @abstractmethod
    async def delete_project(self, project_id: int) -> bool:
        """Delete a project by ID"""
        pass
    
    @abstractmethod
    async def add_project_member(self, project_id: int, user_id: str) -> bool:
        """Add a member to a project"""
        pass
    
    @abstractmethod
    async def remove_project_member(self, project_id: int, user_id: str) -> bool:
        """Remove a member from a project"""
        pass 