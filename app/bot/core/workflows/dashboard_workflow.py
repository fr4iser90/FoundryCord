"""Dashboard workflow for initializing and managing dashboards."""
from typing import Dict, Any, List, Optional
import asyncio
import logging
import nextcord

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from .base_workflow import BaseWorkflow, WorkflowStatus
from app.bot.application.services.dashboard.dashboard_service import DashboardService
from app.shared.domain.repositories import DashboardRepository
from app.shared.infrastructure.database.session.context import session_context
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
            
            # Load existing dashboards for this guild using session context
            guild_dashboards = []
            async with session_context() as session:
                repo = DashboardRepositoryImpl(session)
                all_dashboards = await self.load_dashboards(repo) # Pass repo to load_dashboards
                guild_dashboards = [d for d in all_dashboards if d.guild_id == guild_id]
            
            # Initialize each dashboard
            for dashboard in guild_dashboards:
                try:
                    channel = guild.get_channel(int(dashboard.channel_id))
                    if channel:
                        message = await channel.fetch_message(int(dashboard.message_id))
                        if message:
                            # get_dashboard_config needs a repo instance
                            config = await self.get_dashboard_config(dashboard.dashboard_type) # This uses the repo internally now
                            await self.update_dashboard_message(message, config)
                except nextcord.NotFound:
                     logger.warning(f"Could not find channel {dashboard.channel_id} or message {dashboard.message_id} for dashboard {dashboard.id}. Skipping init.")
                except Exception as e:
                    logger.error(f"Error initializing dashboard {dashboard.id} for guild {guild_id}: {e}", exc_info=True)
            
            # Mark as active
            self.guild_status[guild_id] = WorkflowStatus.ACTIVE
            return True
            
        except Exception as e:
            logger.error(f"Error initializing dashboard workflow for guild {guild_id}: {e}", exc_info=True)
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
    
    async def get_dashboard_config(self, dashboard_type: str) -> Dict[str, Any]:
        """Get complete configuration for a dashboard type"""
        # Use session context to get the repository
        async with session_context() as session:
            repo = DashboardRepositoryImpl(session)
            # The repo method get_dashboard_config doesn't exist, call get_dashboard_by_type instead?
            # Reverting to the old logic of calling get_dashboard_by_type within the repo method
            # Let's assume the repository method handles fetching components itself now.
            try:
                 # Assuming get_dashboard_config needs to be implemented or adjusted in the repo
                 # For now, let's try calling the repo method and see if it works
                 # This method was likely intended to call repo methods internally
                 # Let's try to fetch the dashboard and components manually here if repo lacks get_dashboard_config
                 dashboard = await repo.get_dashboard_by_type(dashboard_type)
                 if not dashboard:
                     logger.warning(f"No dashboard found for type: {dashboard_type}")
                     return {}

                 # Replicate logic previously inside repo.get_dashboard_config
                 config = {
                     "id": dashboard.id,
                     "name": dashboard.name,
                     "type": dashboard.dashboard_type,
                     "components": {}
                 }
                 # This part needs repo.get_components_by_type which also doesn't exist
                 # Need to adjust this logic based on available repo methods
                 # Example: Get all components for the dashboard ID
                 # components = await repo.get_components_by_dashboard(dashboard.id) 
                 # ... then filter/process components ...
                 logger.warning(f"get_dashboard_config needs refactoring - returning basic dashboard info for {dashboard_type}")
                 return {"id": dashboard.id, "name": dashboard.name, "type": dashboard.dashboard_type} # Placeholder return

            except Exception as e:
                logger.error(f"Error getting dashboard config for type {dashboard_type}: {e}", exc_info=True)
                return {}

    async def create_dashboard_message(self, channel: nextcord.TextChannel, dashboard_type: str) -> Optional[nextcord.Message]:
        """Create a new dashboard message in the specified channel"""
        try:
            # Get dashboard configuration first (uses repo internally)
            config = await self.get_dashboard_config(dashboard_type)
            if not config:
                logger.error(f"No configuration found for dashboard type: {dashboard_type}")
                return None
                
            # Create initial message
            message = await channel.send("Dashboard is being prepared...")
            
            # Store the message in the database using session context
            async with session_context() as session:
                repo = DashboardRepositoryImpl(session)
                dashboard = await repo.create_dashboard(
                    name=config.get("name", f"{dashboard_type} Dashboard"), # Use fetched name
                    dashboard_type=dashboard_type,
                    guild_id=str(channel.guild.id),
                    channel_id=str(channel.id), # Ensure channel ID is string
                    message_id=str(message.id) # Ensure message ID is string
                    # Pass other config items if needed by create_dashboard
                )
            
            # Now update the message with proper content
            await self.update_dashboard_message(message, config)
            
            return message
            
        except Exception as e:
            logger.error(f"Error creating dashboard message for type {dashboard_type}: {e}", exc_info=True)
            return None
    
    async def load_dashboards(self, repo: Optional[DashboardRepositoryImpl] = None) -> List: # Accept optional repo
        """Load all dashboards from the repository."""
        dashboards = []
        try:
            if repo: # Use passed repo if available (from initialize_for_guild)
                 dashboards = await repo.get_all_dashboards()
            else: # Otherwise, create a new session and repo
                async with session_context() as session:
                    repo_instance = DashboardRepositoryImpl(session)
                    dashboards = await repo_instance.get_all_dashboards()
                    
            logger.info(f"Loaded {len(dashboards)} dashboards from repository")
            return dashboards
        except Exception as e:
            # Handle specific error if table doesn't exist
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                 logger.warning("Dashboard tables don't exist yet, skipping dashboard load.")
            else:
                logger.error(f"Error retrieving dashboards: {e}", exc_info=True)
            return [] # Return empty list on error

    async def start_background_tasks(self):
        """Start background tasks for dashboards."""
        logger.info("Starting dashboard background tasks")
        # We'll implement dashboard update tasks here
        
    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup resources for a specific guild"""
        logger.info(f"Cleaning up dashboard workflow for guild {guild_id}")
        await super().cleanup_guild(guild_id)
        
        # Remove any dashboards for this guild using session context
        try:
            async with session_context() as session:
                repo = DashboardRepositoryImpl(session)
                dashboards = await repo.get_dashboards_by_guild(guild_id)
                if dashboards:
                     logger.info(f"Deleting {len(dashboards)} dashboards for guild {guild_id}")
                     for dashboard in dashboards:
                        # Assuming delete_dashboard expects the entity object
                        await repo.delete_dashboard(dashboard) 
                     logger.info(f"Finished deleting dashboards for guild {guild_id}")
        except Exception as e:
            logger.error(f"Error cleaning up dashboards for guild {guild_id}: {e}", exc_info=True)
                
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