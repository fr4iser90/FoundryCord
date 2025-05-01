import logging
import nextcord
import asyncio
from typing import Dict, Optional, List
from sqlalchemy import text
import traceback

from app.bot.core.workflows.base_workflow import BaseWorkflow, WorkflowStatus
from app.bot.core.workflows.category_workflow import CategoryWorkflow
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.api import get_session
from app.shared.infrastructure.database.session.context import session_context
from app.shared.domain.repositories.discord import ChannelRepository
from app.shared.domain.repositories.discord import GuildConfigRepository
from app.shared.infrastructure.repositories.discord import ChannelRepositoryImpl
from app.bot.application.services.channel.channel_setup_service import ChannelSetupService
from app.shared.infrastructure.repositories.discord.guild_config_repository_impl import GuildConfigRepositoryImpl
from app.shared.infrastructure.repositories.discord.category_repository_impl import CategoryRepositoryImpl
from app.bot.application.services.channel.channel_builder import ChannelBuilder

logger = get_bot_logger()

class ChannelWorkflow(BaseWorkflow):
    """Workflow for channel setup and management"""
    
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
            logger.info("Initializing channel workflow")
            
            logger.info("Channel workflow initialized globally (no services/repos stored).")
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
            
            # --- Temporarily Disable Old Logic (Already disabled) ---
            logger.warning(f"ChannelWorkflow.initialize_for_guild: Old setup/sync logic for guild {guild_id} is disabled. Structure now comes from templates.")
            # # Set up channels (OLD LOGIC - accesses discord_channels)
            # channels = await self.setup_channels(guild)
            # ...
            # # Sync with Discord (OLD LOGIC)
            # await self.sync_with_discord(guild)
            # --- End Disable ---
            
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
        
    async def setup_channels(self, guild: nextcord.Guild) -> Dict[str, nextcord.TextChannel]:
        """Set up all channels for the guild (Now likely obsolete - Template handles this)"""
        logger.warning("ChannelWorkflow.setup_channels called, but this logic is likely obsolete due to template application.")
        try:
             async with session_context() as session:
                  channel_repo = ChannelRepositoryImpl(session)
                  category_repo = CategoryRepositoryImpl(session)
                  builder = ChannelBuilder(channel_repo, category_repo)
                  setup_service = ChannelSetupService(builder)
                  return await setup_service.setup_channels(guild, session)
        except Exception as e:
            logger.error(f"Error in setup_channels: {e}", exc_info=True)
            return {}
    
    async def sync_with_discord(self, guild: nextcord.Guild) -> None:
        """Sync channels with existing Discord channels (Now likely obsolete)"""
        logger.warning("ChannelWorkflow.sync_with_discord called, but this logic is likely obsolete due to template application.")
        try:
             async with session_context() as session:
                  channel_repo = ChannelRepositoryImpl(session)
                  category_repo = CategoryRepositoryImpl(session)
                  builder = ChannelBuilder(channel_repo, category_repo)
                  setup_service = ChannelSetupService(builder)
                  await setup_service.sync_with_discord(guild, session)
        except Exception as e:
            logger.error(f"Error in sync_with_discord: {e}", exc_info=True)
        
    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup resources for a specific guild"""
        logger.info(f"Cleaning up channel workflow for guild {guild_id}")
        await super().cleanup_guild(guild_id)
