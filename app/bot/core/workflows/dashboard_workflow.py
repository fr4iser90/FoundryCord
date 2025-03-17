"""Dashboard workflow for initializing and managing dashboards."""
from typing import Dict, Any, List, Optional
import asyncio

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.config.constants.dashboard_constants import DASHBOARD_MAPPINGS
from app.bot.infrastructure.factories.service.service_resolver import ServiceResolver
from .base_workflow import BaseWorkflow
#from app.bot.application.services.dashboard import welcome_setup, monitoring_setup, project_setup, gameservers_setup
from app.bot.infrastructure.migrations.dashboard_migration import DashboardMigration
from app.bot.application.services.dashboard.dashboard_service import DashboardService
from app.shared.infrastructure.database.migrations.dashboards.dashboard_components_migration import wait_for_initialization
from app.bot.domain.dashboards.repositories.dashboard_repository import DashboardRepository
from app.shared.infrastructure.database.session import get_session, session_context

class DashboardWorkflow(BaseWorkflow):
    """Workflow for initializing and managing dashboards."""
    
    def __init__(self, bot):
        """Initialize the dashboard workflow.
        
        Args:
            bot: The Discord bot instance
        """
        super().__init__(bot)
        self.dashboard_manager = None
        self.repository = None
        self.service = None
        self.dashboards = []
        
    async def initialize(self):
        """Initialize the dashboard workflow."""
        try:
            logger.info("Initializing dashboard workflow with domain model")
            
            # Wait for database migrations to complete before proceeding
            await wait_for_initialization()
            
            # Create a database session factory for the repository
            session_factory = get_session
            
            # Create repository with session factory
            self.repository = DashboardRepository(session_factory)
            
            # Create service with component and data source registries
            from app.bot.infrastructure.factories.component_registry import ComponentRegistry
            from app.bot.infrastructure.factories.data_source_registry import DataSourceRegistry
            
            component_registry = ComponentRegistry()
            data_source_registry = DataSourceRegistry()
            
            self.service = DashboardService(
                bot=self.bot,
                repository=self.repository,
                component_registry=component_registry,
                data_source_registry=data_source_registry
            )
            
            # Register as global service
            self.bot.register_service('dashboard_service', self.service)
            
            # Initialize dashboard services
            await self._initialize_dashboard_services()
            
            logger.info("Dashboard workflow initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing dashboard workflow: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
            
    async def _initialize_dashboard_services(self):
        """Initialize dashboard services."""
        try:
            logger.info("Initializing dashboard services")
            
            # The specific dashboard service implementations will be loaded here
            # For now, we just use the generic dashboard service
            
            logger.info("Dashboard services initialized")
        except Exception as e:
            logger.error(f"Error initializing dashboard services: {e}")
            raise

    async def load_dashboards(self):
        """Load all dashboards from the repository."""
        try:
            # Check if tables exist first
            try:
                # Attempt to load dashboards if tables exist
                if self.repository:
                    dashboards = await self.repository.get_all_dashboards()
                    logger.info(f"Loaded {len(dashboards)} dashboards from repository")
                    return dashboards
            except Exception as e:
                if "relation" in str(e) and "does not exist" in str(e):
                    logger.warning("Dashboard tables don't exist yet, skipping dashboard load")
                else:
                    logger.error(f"Error retrieving all dashboard configs: {str(e)}")
            
            # Return empty list as fallback
            return []
        except Exception as e:
            logger.error(f"Error in load_dashboards: {str(e)}")
            return []

    async def start_background_tasks(self):
        """Start background tasks for dashboards."""
        logger.info("Starting dashboard background tasks")
        # We'll implement dashboard update tasks here
        
    async def shutdown(self):
        """Clean up resources before shutdown."""
        pass