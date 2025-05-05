import logging
import nextcord
import asyncio
from typing import Dict, Any, Optional, List
from sqlalchemy import text
import traceback
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.application.workflows.base_workflow import BaseWorkflow, WorkflowStatus
from app.bot.application.workflows.category_workflow import CategoryWorkflow
from app.bot.application.workflows.database_workflow import DatabaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.api import get_session
from app.shared.infrastructure.database.session.context import session_context
from app.shared.domain.repositories.discord import ChannelRepository
from app.shared.domain.repositories.discord import GuildConfigRepository
from app.shared.infrastructure.repositories.discord import ChannelRepositoryImpl
from app.shared.infrastructure.repositories.discord.guild_config_repository_impl import GuildConfigRepositoryImpl
from app.shared.infrastructure.repositories.discord.category_repository_impl import CategoryRepositoryImpl
from app.bot.application.services.channel.channel_builder import ChannelBuilder

logger = get_bot_logger()

class ChannelWorkflow(BaseWorkflow):
    """Workflow for channel setup and management
    
    Manages the *state* of channel operations for a guild, but the actual 
    creation/sync logic based on Guild Templates is handled elsewhere 
    (e.g., during template application or a dedicated GuildSyncWorkflow).
    """
    
    def __init__(self, database_workflow: DatabaseWorkflow, category_workflow: CategoryWorkflow, bot):
        super().__init__("channel")
        self.category_workflow = category_workflow
        self.database_workflow = database_workflow
        self.bot = bot
        
        # Define dependencies
        self.add_dependency("category")
        self.add_dependency("database")
        
        # Channels require guild approval
        self.requires_guild_approval = True
    
    async def initialize(self) -> bool:
        """Initialize the channel workflow globally"""
        try:
            logger.debug("Initializing channel workflow")
            
            logger.debug("Channel workflow initialized globally (no services/repos stored).")
            return True # Return True outside the try/except for session
            
        except Exception as e:
            logger.error(f"Channel workflow initialization failed: {e}", exc_info=True)
            # traceback.print_exc() # Handled by exc_info=True
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
                
            # Check if channels are enabled for this guild (Now done via GuildConfig repo)
            try:
                async with session_context() as session:
                    guild_config_repo = GuildConfigRepositoryImpl(session)
                    config = await guild_config_repo.get_by_guild_id(str(guild.id))
                    
                    if not config:
                         logger.warning(f"No GuildConfig found for guild {guild_id}, cannot determine channel settings (assuming enabled)." )
                         
            except Exception as session_err:
                 logger.error(f"Failed to get session or check guild config in ChannelWorkflow for guild {guild_id}: {session_err}", exc_info=True)
                 self.guild_status[guild_id] = WorkflowStatus.FAILED
                 return False
            
            # --- Guild Template Application is Handled Elsewhere ---
            # The old logic for setup_channels and sync_with_discord within this workflow 
            # has been removed as it's obsolete. The source of truth is now the Guild Template,
            # applied via a different process (e.g., GuildSyncWorkflow or template application command).
            logger.warning(f"ChannelWorkflow.initialize_for_guild: Guild {guild_id} channel structure comes from applied template. Workflow only manages state.")
            # --- End --- 
            
            # Mark as active (conceptually, it's ready if guild is approved)
            self.guild_status[guild_id] = WorkflowStatus.ACTIVE
            return True
            
        except Exception as e:
            logger.error(f"Error initializing channel workflow for guild {guild_id}: {e}")
            self.guild_status[guild_id] = WorkflowStatus.FAILED
            return False
    
    async def cleanup(self) -> None:
        """Cleanup all resources"""
        logger.info("Cleaning up channel workflow")
        await super().cleanup()
        
    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup resources for a specific guild"""
        logger.info(f"Cleaning up channel workflow for guild {guild_id}")
        await super().cleanup_guild(guild_id)
