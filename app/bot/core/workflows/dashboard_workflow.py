"""Dashboard workflow for initializing and managing dashboards."""
from typing import Dict, Any, List, Optional
import asyncio
import logging
import discord

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.config.constants.dashboard_constants import DASHBOARD_MAPPINGS
from app.bot.infrastructure.factories.service.service_resolver import ServiceResolver
from .base_workflow import BaseWorkflow
from app.bot.application.services.dashboard.dashboard_service import DashboardService
from app.shared.infrastructure.database.migrations.dashboards.dashboard_components_migration import wait_for_initialization
from app.bot.domain.dashboards.repositories.dashboard_repository import DashboardRepository
from app.shared.infrastructure.database.session import get_session, session_context
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.infrastructure.database.repositories.dashboard_repository_impl import DashboardRepository

class DashboardWorkflow(BaseWorkflow):
    """Workflow for managing dashboard components and integration"""
    
    def __init__(self, database_workflow: DatabaseWorkflow):
        super().__init__()
        self.name = "dashboard"
        self.database_workflow = database_workflow
        self.dashboard_repository = None
        
    async def initialize(self):
        """Initialize the dashboard workflow"""
        logger.info("Initializing dashboard workflow")
        
        # Get the database service
        db_service = self.database_workflow.get_db_service()
        if not db_service:
            logger.error("Database service not available, cannot initialize dashboard workflow")
            return False
        
        # Create async session
        session = await db_service.async_session()
        
        # Create the repository
        self.dashboard_repository = DashboardRepository(session)
        
        logger.info("Dashboard workflow initialized successfully")
        return True
    
    async def cleanup(self):
        """Cleanup resources used by the dashboard workflow"""
        logger.info("Cleaning up dashboard workflow resources")
        # Reset the repository reference
        self.dashboard_repository = None
        
    async def get_dashboard_config(self, dashboard_type: str) -> Dict[str, Any]:
        """Get complete configuration for a dashboard type"""
        if not self.dashboard_repository:
            logger.error("Dashboard repository not initialized")
            return {}
            
        return await self.dashboard_repository.get_dashboard_config(dashboard_type)
    
    async def create_dashboard_message(self, channel: discord.TextChannel, dashboard_type: str) -> Optional[discord.Message]:
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