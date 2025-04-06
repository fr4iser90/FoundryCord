"""Dashboard workflow for initializing and managing dashboards."""
from typing import Dict, Any, List, Optional
import asyncio
import logging
import nextcord

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.config.constants.dashboard_constants import DASHBOARD_MAPPINGS
from app.bot.infrastructure.factories.service.service_resolver import ServiceResolver
from .base_workflow import BaseWorkflow, WorkflowStatus
from app.bot.application.services.dashboard.dashboard_service import DashboardService
from app.shared.domain.repositories import DashboardRepository
from app.shared.infrastructure.database.core.config import get_session
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.infrastructure.repositories.discord.dashboard_repository_impl import DashboardRepositoryImpl
from app.bot.infrastructure.factories.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.data_source_registry import DataSourceRegistry

class DashboardWorkflow(BaseWorkflow):
    """Workflow for managing dashboard components and integration"""
    
    def __init__(self, database_workflow: DatabaseWorkflow, bot=None):
        super().__init__("dashboard")
        self.database_workflow = database_workflow
        self.dashboard_service = None
        self.dashboard_repository = None
        self.component_registry = None
        self.data_source_registry = None
        self.bot = bot
        
        # Add dependencies
        self.add_dependency("database")
        
        # Dashboards require guild approval
        self.requires_guild_approval = True
        
    async def initialize(self) -> bool:
        """Initialize dashboard workflow globally"""
        try:
            logger.info("Initializing dashboard workflow")
            
            # Get database service from the database workflow
            db_service = self.database_workflow.get_db_service()
            if not db_service:
                logger.error("Database service not available, cannot initialize dashboard workflow")
                return False
            
            # Implementierung verwenden, aber Interface-Typ deklarieren
            self.dashboard_repository: DashboardRepository = DashboardRepositoryImpl(db_service)
            
            # Initialize registries
            self.component_registry = ComponentRegistry()
            self.data_source_registry = DataSourceRegistry()
            
            # Initialize service
            self.dashboard_service = DashboardService(
                db_service, 
                self.bot,
                self.component_registry,
                self.data_source_registry
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Dashboard workflow initialization failed: {e}")
            return False
            
    async def initialize_for_guild(self, guild_id: str) -> bool:
        """Initialize workflow for a specific guild"""
        try:
            # Update status to initializing
            self.guild_status[guild_id] = WorkflowStatus.INITIALIZING
            
            # Get the guild
            if not self.bot:
                logger.error("Bot instance not available")
                self.guild_status[guild_id] = WorkflowStatus.FAILED
                return False
                
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id}")
                self.guild_status[guild_id] = WorkflowStatus.FAILED
                return False
            
            # Load existing dashboards for this guild
            dashboards = await self.load_dashboards()
            guild_dashboards = [d for d in dashboards if d.guild_id == guild_id]
            
            # Initialize each dashboard
            for dashboard in guild_dashboards:
                try:
                    channel = guild.get_channel(int(dashboard.channel_id))
                    if channel:
                        message = await channel.fetch_message(int(dashboard.message_id))
                        if message:
                            config = await self.get_dashboard_config(dashboard.dashboard_type)
                            await self.update_dashboard_message(message, config)
                except Exception as e:
                    logger.error(f"Error initializing dashboard {dashboard.id} for guild {guild_id}: {e}")
            
            # Mark as active
            self.guild_status[guild_id] = WorkflowStatus.ACTIVE
            return True
            
        except Exception as e:
            logger.error(f"Error initializing dashboard workflow for guild {guild_id}: {e}")
            self.guild_status[guild_id] = WorkflowStatus.FAILED
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources used by the dashboard workflow"""
        logger.info("Cleaning up dashboard workflow resources")
        
        try:
            # Cleanup dashboard service
            if self.dashboard_service and hasattr(self.dashboard_service, 'cleanup'):
                await self.dashboard_service.cleanup()
            
            await super().cleanup()
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
        
    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup resources for a specific guild"""
        logger.info(f"Cleaning up dashboard workflow for guild {guild_id}")
        await super().cleanup_guild(guild_id)
        
        # Remove any dashboards for this guild
        if self.dashboard_repository:
            try:
                dashboards = await self.dashboard_repository.get_dashboards_by_guild(guild_id)
                for dashboard in dashboards:
                    await self.dashboard_repository.delete_dashboard(dashboard.id)
            except Exception as e:
                logger.error(f"Error cleaning up dashboards for guild {guild_id}: {e}")
                
    async def update_dashboard_message(self, message: nextcord.Message, config: Dict[str, Any]) -> None:
        """Update a dashboard message with new content based on config"""
        try:
            # This is a placeholder - implement actual message update logic
            await message.edit(content="Dashboard updated")
        except Exception as e:
            logger.error(f"Error updating dashboard message: {e}")
            
    async def shutdown(self):
        """Clean up resources before shutdown."""
        await self.cleanup()