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

class DashboardWorkflow(BaseWorkflow):
    """Workflow for initializing and managing dashboards."""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.dashboard_manager = None
        
    async def initialize(self):
        """Initialize the dashboard workflow."""
        try:
            # Initialize dashboard service
            self.dashboard_service = DashboardService(self.bot)
            
            # Initialize dashboard manager
            logger.info("Initializing dashboard workflow")
            
            # Initialize dashboard repository
            logger.info("Initializing dashboard repository")
            dashboard_repo = {
                'name': 'dashboard_repository',
                'type': 'dashboard_repository' 
            }
            repository = await self.bot.lifecycle._initialize_service(dashboard_repo)
            
            if not repository:
                logger.error("Failed to initialize dashboard repository")
                return False
                
            # Initialize dashboard builder service
            logger.info("Initializing dashboard builder service")
            dashboard_builder = {
                'name': 'dashboard_builder',
                'type': 'dashboard_builder'
            }
            builder = await self.bot.lifecycle._initialize_service(dashboard_builder)
            
            if not builder:
                logger.error("Failed to initialize dashboard builder")
                return False
                
            # Get dashboard manager from bot
            self.dashboard_manager = getattr(self.bot, 'dashboard_manager', None)
            if not self.dashboard_manager:
                logger.error("Dashboard manager not found")
                return False
                
            # Run dashboard migration
            await self._run_dashboard_migration()
                
            # Activate initial dashboards
            await self._activate_initial_dashboards()
                
            logger.info("Dashboard workflow initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize dashboard workflow: {e}")
            return False
            
    async def _run_dashboard_migration(self):
        """Run dashboard migration if needed."""
        try:
            # Check if we need to migrate
            migration = DashboardMigration(self.bot)
            await migration.initialize()
            
            # Create welcome dashboard if it doesn't exist
            welcome_created = await migration.create_welcome_dashboard()
            if welcome_created:
                logger.info("Welcome dashboard created")
                
            return True
            
        except Exception as e:
            logger.error(f"Error running dashboard migration: {e}")
            return False
            
    async def _activate_initial_dashboards(self):
        """Activate initial dashboards."""
        try:
            # This would normally fetch and activate dashboards from the database
            # For now, we'll just wait for the migration to handle it
            logger.info("Initial dashboards activated")
            return True
            
        except Exception as e:
            logger.error(f"Error activating initial dashboards: {e}")
            return False
    
    async def cleanup(self):
        """Clean up dashboard resources."""
        try:
            if self.dashboard_manager:
                # Deactivate all dashboards
                # This is a simple implementation - in a real application,
                # we'd properly track which channels have active dashboards
                logger.info("Dashboard workflow cleaned up")
                
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up dashboard workflow: {e}")
            return False

    async def execute(self) -> None:
        """Initialize all dashboard services"""
        try:
            logger.info("Initializing dashboard services...")
            
            # OLD NO HARDCODED DASHBOARDS ANYMORE
            # Initialize existing dashboard services
            #self.bot.welcome_dashboard_service = await welcome_setup(self.bot)
            #self.bot.monitoring_dashboard_service = await monitoring_setup(self.bot)
            #self.bot.project_dashboard_service = await project_setup(self.bot)
            #self.bot.gamehub_dashboard_service = await gameservers_setup(self.bot)
            
            
            logger.info("Dashboard services initialized")
        except Exception as e:
            logger.error(f"Error initializing dashboard services: {e}")
            raise