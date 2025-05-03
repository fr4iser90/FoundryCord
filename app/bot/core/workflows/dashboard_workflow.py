"""Dashboard workflow for initializing and managing dashboards."""
from typing import Dict, Any, List, Optional
import asyncio
import logging
import nextcord

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from .base_workflow import BaseWorkflow, WorkflowStatus
from app.shared.domain.repositories import DashboardRepository
from app.shared.infrastructure.database.session.context import session_context
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.infrastructure.repositories.discord.dashboard_repository_impl import DashboardRepositoryImpl

class DashboardWorkflow(BaseWorkflow):
    """Workflow for managing dashboard state.
    
    Handles the status tracking for dashboard operations within guilds.
    The actual activation, lifecycle, and rendering of dashboards are managed 
    by DashboardLifecycleService, DashboardRegistry, and DashboardController.
    """
    
    def __init__(self, database_workflow: DatabaseWorkflow, bot=None):
        super().__init__("dashboard")
        self.database_workflow = database_workflow
        self.bot = bot
        
        # Add dependencies
        self.add_dependency("database")
        
        # Dashboards require guild approval
        self.requires_guild_approval = True
        
    async def initialize(self) -> bool:
        """Initialize dashboard workflow globally"""
        try:
            logger.info("Initializing dashboard workflow (state management only)")
            # No complex service/registry initialization needed here.
            # LifecycleService handles the actual dashboard setup.
            return True
            
        except Exception as e:
            logger.error(f"Dashboard workflow initialization failed: {e}")
            return False
            
    async def initialize_for_guild(self, guild_id: str) -> bool:
        """Initialize workflow state for a specific guild"""
        try:
            # Update status to initializing
            self.guild_status[guild_id] = WorkflowStatus.INITIALIZING
            
            # Get the guild (basic check)
            if not self.bot:
                logger.error("Bot instance not available for DashboardWorkflow")
                self.guild_status[guild_id] = WorkflowStatus.FAILED
                return False
                
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id} in DashboardWorkflow")
                self.guild_status[guild_id] = WorkflowStatus.FAILED
                return False
            
            # Mark as active (workflow state is ready, actual dashboards handled by LifecycleService)
            logger.info(f"DashboardWorkflow state set to ACTIVE for guild {guild_id}. LifecycleService handles activation.")
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
            await super().cleanup()
            logger.info("Dashboard workflow resources cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up dashboard workflow: {e}")
    
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