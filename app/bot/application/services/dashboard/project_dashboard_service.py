from typing import Dict, List, Optional, Any
from datetime import datetime
from app.bot.infrastructure.logging import logger
from app.bot.infrastructure.database.models import Project, Task
from app.bot.infrastructure.database.repositories.project_repository_impl import ProjectRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.infrastructure.database.models.config import get_session
import nextcord
from app.bot.interfaces.dashboards.controller.project_dashboard import ProjectDashboardController

class ProjectDashboardService:
    """Service for the Project Dashboard business logic"""
    
    def __init__(self, bot):
        self.bot = bot
        self.initialized = False
        self.project_repo = None  # Wird in initialize() gesetzt
        self.embed_factory = bot.component_factory.factories.get('embed')
        self.dashboard_ui = None
        self.db_service = None  # Will reference database service
    
    async def initialize(self) -> None:
        """Initialize the service"""
        try:
            # Initialize project repository directly instead of getting DB service
            async for session in get_session():
                self.project_repo = ProjectRepository(session)
                break  # Just need one session to create the repository
            
            # Initialize UI component - make sure we're creating a new instance
            self.dashboard_ui = ProjectDashboardController(self.bot)
            # Important: set_service must return self for method chaining
            self.dashboard_ui.set_service(self)
            
            # Only call initialize if dashboard_ui is not None
            if self.dashboard_ui:
                await self.dashboard_ui.initialize()
                self.initialized = True
                logger.info("Project Dashboard Service initialized")
            else:
                logger.error("Failed to create dashboard UI")
        except Exception as e:
            logger.error(f"Error initializing Project Dashboard Service: {e}")
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

    async def display_dashboard(self) -> None:
        """Display the project dashboard"""
        try:
            if not self.dashboard_ui:
                logger.error("Dashboard UI not initialized")
                return
                
            await self.dashboard_ui.display_dashboard()
            logger.info("Project dashboard displayed successfully")
        except Exception as e:
            logger.error(f"Error displaying project dashboard: {e}")

async def setup(bot):
    """Setup function for the Project Dashboard service"""
    try:
        logger.debug("Creating Project Dashboard Service")
        service = ProjectDashboardService(bot)
        
        logger.debug("Initializing Project Dashboard Service")
        await service.initialize()
        
        # Only display if initialization worked
        if service.initialized:
            logger.debug("Displaying Project Dashboard")
            try:
                await service.display_dashboard()
            except Exception as display_error:
                logger.error(f"Error displaying Project Dashboard: {display_error}")
        
        logger.info("Project Dashboard service initialized successfully")
        return service  # Return service object
    except Exception as e:
        logger.error(f"Failed to initialize Project Dashboard service: {e}")
        # Don't raise - return None so service factory can continue
        return None