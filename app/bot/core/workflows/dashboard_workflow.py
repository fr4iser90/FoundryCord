"""Dashboard workflow for initializing and managing dashboards."""
from typing import Dict, Any, List, Optional
import asyncio
import logging
import nextcord

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.config.constants.dashboard_constants import DASHBOARD_MAPPINGS
from app.bot.infrastructure.factories.service.service_resolver import ServiceResolver
from .base_workflow import BaseWorkflow
from app.bot.application.services.dashboard.dashboard_service import DashboardService
from app.shared.infrastructure.database.migrations.dashboards.dashboard_components_migration import wait_for_initialization
from app.bot.domain.dashboards.repositories.dashboard_repository import DashboardRepository
from app.shared.infrastructure.database.core.config import get_session
, session_context
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.infrastructure.database.repositories.dashboard_repository_impl import DashboardRepository
from app.bot.infrastructure.factories.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.data_source_registry import DataSourceRegistry

class DashboardWorkflow(BaseWorkflow):
    """Workflow for managing dashboard components and integration"""
    
    def __init__(self, database_workflow: DatabaseWorkflow, bot=None):
        super().__init__(bot)
        self.name = "dashboard"
        self.database_workflow = database_workflow
        self.dashboard_service = None
        self.dashboard_repository = None
        self.component_registry = None
        self.data_source_registry = None
        self.bot = bot
        
        # Add dependencies
        self.add_dependency("database")
        
    async def initialize(self):
        """Initialize the dashboard workflow"""
        logger.info("Initializing dashboard workflow")
        
        try:
            # Get database service
            db_service = self.database_workflow.get_db_service()
            if not db_service:
                logger.error("Database service not available, cannot initialize dashboard workflow")
                return False
            
            # Import repositories and services
            from app.bot.infrastructure.repositories.dashboard_repository_impl import DashboardRepositoryImpl
            from app.bot.application.services.dashboard.dashboard_service import DashboardService
            
            # Initialize repository
            self.dashboard_repository = DashboardRepositoryImpl(db_service)
            
            # Initialize registries
            self.component_registry = ComponentRegistry()
            self.data_source_registry = DataSourceRegistry()
            
            # Überprüfen, ob der Bot verfügbar ist
            if not self.bot:
                logger.error("Bot instance not available, cannot initialize dashboard service")
                return False
            
            # Initialize service with all required parameters
            self.dashboard_service = DashboardService(
                repository=self.dashboard_repository,
                component_registry=self.component_registry,
                data_source_registry=self.data_source_registry,
                bot=self.bot
            )
            
            logger.info("Dashboard workflow initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing dashboard workflow: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def cleanup(self):
        """Cleanup resources used by the dashboard workflow"""
        logger.info("Cleaning up dashboard workflow resources")
        
        try:
            # Cleanup dashboard service
            if self.dashboard_service and hasattr(self.dashboard_service, 'cleanup'):
                await self.dashboard_service.cleanup()
            
            logger.info("Dashboard workflow resources cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up dashboard workflow: {e}")
    
    async def get_dashboard_service(self):
        """Get the dashboard service"""
        return self.dashboard_service
    
    async def get_dashboard_repository(self):
        """Get the dashboard repository"""
        return self.dashboard_repository
    
    async def get_dashboard_config(self, dashboard_type: str) -> Dict[str, Any]:
        """Get complete configuration for a dashboard type"""
        if not self.dashboard_repository:
            logger.error("Dashboard repository not initialized")
            return {}
            
        return await self.dashboard_repository.get_dashboard_config(dashboard_type)
    
    async def create_dashboard_message(self, channel: nextcord.TextChannel, dashboard_type: str) -> Optional[nextcord.Message]:
        """Create a new dashboard message in the specified channel"""
        if not self.dashboard_repository:
            logger.error("Dashboard repository not initialized")
            return None
            
        # Get dashboard configuration
        config = await self.get_dashboard_config(dashboard_type)
        if not config:
            logger.error(f"No configuration found for dashboard type: {dashboard_type}")
            return None
            
        # Create initial message
        try:
            message = await channel.send("Dashboard is being prepared...")
            
            # Store the message in the database
            dashboard = await self.dashboard_repository.create_dashboard(
                title=config.get("title", "Dashboard"),
                dashboard_type=dashboard_type,
                guild_id=str(channel.guild.id),
                channel_id=channel.id,
                message_id=message.id
            )
            
            # Now update the message with proper content
            # This would generate the message content, embeds, buttons, etc. based on config
            await self.update_dashboard_message(message, config)
            
            return message
            
        except Exception as e:
            logger.error(f"Error creating dashboard message: {e}")
            return None
    
    async def load_dashboards(self):
        """Load all dashboards from the repository."""
        try:
            # Check if tables exist first
            try:
                # Attempt to load dashboards if tables exist
                if self.dashboard_repository:
                    dashboards = await self.dashboard_repository.get_all_dashboards()
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