from typing import Dict, List, Optional, Any
from datetime import datetime
from infrastructure.logging import logger
from infrastructure.database.models.models import Project, Task
from infrastructure.database.repositories.project_repository import ProjectRepository
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models.config import get_session
from nextcord.ext import commands
import nextcord

class ProjectDashboardService(commands.Cog):
    """Service für die Geschäftslogik des Project Dashboards"""
    
    def __init__(self, bot):
        self.bot = bot
        self.initialized = False
        self.project_repo = None  # Wird in initialize() gesetzt
        super().__init__()
    
    async def initialize(self) -> None:
        """Initialisiert den Service"""
        try:
            # Initialisiere Repository mit Session
            async for session in get_session():
                self.project_repo = ProjectRepository(session)
                await self.project_repo.get_all()  # Test query
                
            self.initialized = True
            logger.info("Project Dashboard Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Project Dashboard Service: {e}")
            raise
    
    async def get_projects_by_status(self) -> Dict[str, List[Project]]:
        """Holt alle Projekte gruppiert nach Status"""
        try:
            projects = await self.get_all_projects()  # Nutze die neue Methode
            
            # Gruppiere nach Status
            projects_by_status = {}
            for project in projects:
                if project.status not in projects_by_status:
                    projects_by_status[project.status] = []
                projects_by_status[project.status].append(project)
            
            return projects_by_status
        except Exception as e:
            logger.error(f"Error getting projects by status: {e}")
            return {}
    
    async def get_project(self, project_id: int) -> Optional[Project]:
        """Holt ein einzelnes Projekt mit allen Tasks"""
        try:
            async for session in get_session():
                project_repo = ProjectRepository(session)
                project = await project_repo.get_by_id(project_id)
                # Eager loading der Tasks
                if project:
                    await session.refresh(project, ['tasks'])
                return project
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {e}")
            return None
    
    async def create_project(self, name: str, description: str, created_by: Optional[str] = None, **kwargs):
        try:
            project = await self.project_repo.create(
                name=name,
                description=description,
                status=kwargs.get('status', 'planning'),
                priority=kwargs.get('priority', 'medium'),
                created_by=created_by
            )
            return project
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise
    
    async def update_project(self, project: Project) -> Project:
        """Aktualisiert ein bestehendes Projekt"""
        async with async_session() as session:
            project_repo = ProjectRepository(session)
            return await project_repo.update(project)
    
    async def delete_project(self, project: Project) -> bool:
        """Löscht ein Projekt"""
        async with async_session() as session:
            project_repo = ProjectRepository(session)
            await project_repo.delete(project)
            return True
    
    async def update_project_status(self, project: Project, new_status: str) -> Project:
        """Aktualisiert den Status eines Projekts"""
        if not hasattr(project, 'status'):
            raise AttributeError("Das Projektmodell unterstützt kein 'status'-Attribut")
            
        project.status = new_status
        return await self.update_project(project)

    async def get_all_projects(self) -> List[Project]:
        """Holt alle Projekte mit ihren Tasks"""
        try:
            async for session in get_session():
                project_repo = ProjectRepository(session)
                projects = await project_repo.get_all()
                # Eager loading der Tasks für alle Projekte
                for project in projects:
                    await session.refresh(project, ['tasks'])
                return projects
        except Exception as e:
            logger.error(f"Error getting all projects: {e}")
            return []