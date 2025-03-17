import logging
import nextcord
import asyncio
from typing import Dict, Optional, List
from sqlalchemy import text

from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.bot.core.workflows.category_workflow import CategoryWorkflow
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.interface.logging.api import get_bot_logger

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
        logger.info("Initializing channel workflow")
        
        try:
            # Get the database service
            db_service = self.database_workflow.get_db_service()
            if not db_service:
                logger.error("Database service not available, cannot initialize channel workflow")
                return False
                
            # Import repositories and services
            from app.bot.infrastructure.repositories.channel_repository_impl import ChannelRepositoryImpl
            from app.bot.application.services.channel.channel_builder import ChannelBuilder
            from app.bot.application.services.channel.channel_setup_service import ChannelSetupService
            from app.shared.infrastructure.database.migrations.channels.seed_channels import seed_channels
            
            # Get category repository from category workflow
            category_repository = self.category_workflow.get_category_repository()
            if not category_repository:
                logger.error("Category repository not available, cannot initialize channel workflow")
                return False
            
            # Create repository
            self.channel_repository = ChannelRepositoryImpl(db_service)
            
            # Create channel builder with both repositories
            channel_builder = ChannelBuilder(
                self.channel_repository,
                category_repository  # Pass the category repository here
            )
            
            # Create channel setup service
            self.channel_setup_service = ChannelSetupService(
                self.channel_repository, 
                channel_builder,
                self.category_workflow
            )
            
            # Check if channels exist, if not seed the database
            engine = db_service.get_engine()
            try:
                channels_exist = False
                async with engine.connect() as conn:
                    result = await conn.execute(text("SELECT COUNT(*) FROM channels"))
                    row = result.first()
                    count = row[0] if row else 0
                    channels_exist = count > 0
                
                if not channels_exist:
                    logger.info("No channels found in database, seeding default channels")
                    seed_channels()
                    logger.info("Default channels seeded successfully")
            except Exception as e:
                logger.error(f"Error checking/seeding channels: {e}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error initializing workflow channel: {e}")
            import traceback
            logger.error(traceback.format_exc())
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
