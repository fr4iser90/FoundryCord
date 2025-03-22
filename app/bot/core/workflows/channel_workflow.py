import logging
import nextcord
import asyncio
from typing import Dict, Optional, List
from sqlalchemy import text
import traceback

from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.bot.core.workflows.category_workflow import CategoryWorkflow
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.api import get_session
from app.shared.infrastructure.database.session.context import session_context
from app.shared.domain.repositories.discord import ChannelRepository
from app.shared.infrastructure.repositories.guild_config_repository_impl import GuildConfigRepository

logger = get_bot_logger()

class ChannelWorkflow(BaseWorkflow):
    """Workflow for channel setup and management"""
    
    def __init__(self, category_workflow: CategoryWorkflow, database_workflow: DatabaseWorkflow):
        super().__init__()
        self.name = "channel"
        self.category_workflow = category_workflow
        self.database_workflow = database_workflow
        self.channel_repository = None
        self.channel_setup_service = None
        
        # Define dependencies
        self.add_dependency("category")
        self.add_dependency("database")
    
    async def initialize(self):
        """Initialize the channel workflow"""
        try:
            logger.info("Initializing channel workflow")
            
            # Get database service from the database workflow
            db_service = self.database_workflow.get_db_service()
            if not db_service:
                logger.error("Database service not available, cannot initialize channel workflow")
                return False
            
            # Create repository and service
            self.channel_repository = ChannelRepository(db_service)
            self.channel_setup_service = ChannelSetupService(
                self.channel_repository, 
                self.category_workflow.get_category_repository()
            )
            
            # Verify channel data exists
            channel_count = await self.channel_repository.count()
            logger.info(f"Found {channel_count} channels")
            
            return True
            
        except Exception as e:
            logger.error(f"Channel workflow initialization failed: {e}")
            traceback.print_exc()
            return False
    
    async def cleanup(self):
        """Cleanup resources used by the channel workflow"""
        logger.info("Cleaning up channel workflow resources")
        # Nothing to clean up for now
        
    async def setup_channels(self, guild: nextcord.Guild) -> Dict[str, nextcord.TextChannel]:
        """Set up all channels for the guild"""
        if not self.channel_setup_service:
            logger.error("Channel setup service not initialized")
            return {}
            
        # Check if this workflow is enabled for this guild
        async with session_context() as session:
            guild_config_repo = GuildConfigRepository(session)
            config = await guild_config_repo.get_by_guild_id(str(guild.id))
            
            if not config or not config.enable_channels:
                logger.info(f"Channel workflow is disabled for guild: {guild.name}")
                return {}
        
        logger.info(f"Setting up channels for guild: {guild.name}")
        return await self.channel_setup_service.setup_channels(guild)
    
    async def sync_with_discord(self, guild: nextcord.Guild) -> None:
        """Sync channels with existing Discord channels"""
        if not self.channel_setup_service:
            logger.error("Channel setup service not initialized")
            return
            
        logger.info(f"Syncing channels with Discord for guild: {guild.name}")
        await self.channel_setup_service.sync_with_discord(guild)

    def get_channel_repository(self):
        """Get the channel repository"""
        return self.channel_repository
    
    def get_channel_setup_service(self):
        """Get the channel setup service"""
        return self.channel_setup_service
