import logging
import nextcord
import asyncio
from typing import Dict, Optional, List
from sqlalchemy import text
import traceback

from app.bot.core.workflows.base_workflow import BaseWorkflow, WorkflowStatus
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session.context import session_context
from app.shared.domain.repositories.discord.category_repository import CategoryRepository
from app.shared.infrastructure.repositories.discord import CategoryRepositoryImpl

logger = get_bot_logger()

class CategoryWorkflow(BaseWorkflow):
    """Workflow for category setup and management

    Manages the *state* of category operations for a guild, but the actual 
    creation/sync logic based on Guild Templates is handled elsewhere 
    (e.g., during template application or a dedicated GuildSyncWorkflow).
    """
    
    def __init__(self, database_workflow: DatabaseWorkflow, bot):
        super().__init__("category")
        self.database_workflow = database_workflow
        self.bot = bot
        
        # Define dependencies
        self.add_dependency("database")
        
        # Categories require guild approval
        self.requires_guild_approval = True
    
    async def initialize(self) -> bool:
        """Initialize the category workflow globally"""
        try:
            # No global service instantiation needed anymore. 
            # Services are instantiated temporarily when needed or managed elsewhere.
            logger.info("Category workflow initialized globally (stateless).")
            return True

        except Exception as e:
            logger.error(f"Error initializing category workflow: {e}", exc_info=True)
            return False
            
    async def initialize_for_guild(self, guild_id: str) -> bool:
        """Initialize workflow for a specific guild"""
        try:
            # Update status to initializing
            self.guild_status[guild_id] = WorkflowStatus.INITIALIZING
            
            # Get the guild
            if not hasattr(self, 'bot') or not self.bot:
                logger.error("Bot instance not available")
                self.guild_status[guild_id] = WorkflowStatus.FAILED
                return False
                
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id}")
                self.guild_status[guild_id] = WorkflowStatus.FAILED
                return False
            
            # --- Guild Template Application is Handled Elsewhere ---
            # The old logic for setup_categories and sync_with_discord within this workflow 
            # has been removed as it's obsolete. The source of truth is now the Guild Template,
            # applied via a different process (e.g., GuildSyncWorkflow or template application command).
            logger.warning(f"CategoryWorkflow.initialize_for_guild: Guild {guild_id} category structure comes from applied template. Workflow only manages state.")
            # --- End --- 
            
            # Mark as active (conceptually, it's ready if guild is approved)
            self.guild_status[guild_id] = WorkflowStatus.ACTIVE
            return True
            
        except Exception as e:
            logger.error(f"Error initializing category workflow for guild {guild_id}: {e}")
            self.guild_status[guild_id] = WorkflowStatus.FAILED
            return False
    
    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup resources for a specific guild"""
        logger.info(f"Cleaning up category workflow for guild {guild_id}")
        await super().cleanup_guild(guild_id)
        # No specific cache cleanup needed here anymore
            
    async def cleanup(self) -> None:
        """Cleanup all resources"""
        logger.info("Cleaning up category workflow")
        await super().cleanup()
        # No specific cache cleanup needed here anymore
