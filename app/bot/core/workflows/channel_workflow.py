import logging
import nextcord
import asyncio
from typing import Dict, Optional, List
from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.bot.core.workflows.category_workflow import CategoryWorkflow
from app.bot.domain.channels.repositories.channel_repository import ChannelRepository
from app.bot.infrastructure.repositories.channel_repository_impl import ChannelRepositoryImpl
from app.bot.application.services.channel.channel_builder import ChannelBuilder
from app.bot.application.services.channel.channel_setup_service import ChannelSetupService
from app.bot.application.services.channel.channel_factory import ChannelFactory
from app.shared.infrastructure.database.migrations.channels.seed_channels import seed_channels

logger = logging.getLogger("homelab.bot")

class ChannelWorkflow(BaseWorkflow):
    """Workflow for channel setup and management"""
    
    def __init__(self, database_workflow: DatabaseWorkflow, category_workflow: CategoryWorkflow):
        super().__init__()
        self.name = "channel"
        self.database_workflow = database_workflow
        self.category_workflow = category_workflow
        self.channel_repository = None
        self.channel_setup_service = None
        self.channel_factory = None
    
    async def initialize(self):
        """Initialize the channel workflow"""
        logger.info("Initializing channel workflow")
        
        # Get the database service
        db_service = self.database_workflow.get_db_service()
        if not db_service:
            logger.error("Database service not available, cannot initialize channel workflow")
            return False
        
        # Get the category repository and setup service
        category_repository = self.category_workflow.get_category_repository()
        category_setup_service = self.category_workflow.get_category_setup_service()
        
        if not category_repository or not category_setup_service:
            logger.error("Category services not available, cannot initialize channel workflow")
            return False
        
        # Initialize the channel repository
        self.channel_repository = ChannelRepositoryImpl(db_service)
        
        # Initialize the channel builder
        channel_builder = ChannelBuilder(self.channel_repository, category_repository)
        
        # Initialize the channel setup service
        self.channel_setup_service = ChannelSetupService(
            self.channel_repository, 
            category_repository,
            category_setup_service
        )
        
        # Initialize the channel factory
        self.channel_factory = ChannelFactory(
            self.channel_repository,
            category_repository,
            channel_builder
        )
        
        # Seed the default channels if database is empty
        await self.seed_channels_if_empty()
        
        logger.info("Channel workflow initialized successfully")
        return True
    
    async def seed_channels_if_empty(self):
        """Seed default channels if none exist in the database"""
        channels = self.channel_repository.get_all_channels()
        
        if not channels:
            logger.info("No channels found in database, seeding default channels")
            # Use the seed function from the migration script
            seed_channels()
            logger.info("Default channels seeded successfully")
    
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
    
    def get_channel_repository(self) -> Optional[ChannelRepository]:
        """Get the channel repository"""
        return self.channel_repository
    
    def get_channel_setup_service(self) -> Optional[ChannelSetupService]:
        """Get the channel setup service"""
        return self.channel_setup_service
    
    def get_channel_factory(self) -> Optional[ChannelFactory]:
        """Get the channel factory"""
        return self.channel_factory
    
    async def create_game_server_channel(
        self, 
        guild: nextcord.Guild, 
        game_name: str,
        category_name: str = "GAME SERVERS"
    ) -> Optional[nextcord.TextChannel]:
        """Create a game server channel"""
        if not self.channel_factory:
            logger.error("Channel factory not initialized")
            return None
        
        logger.info(f"Creating game server channel for: {game_name}")
        return await self.channel_factory.create_game_server_channel(
            guild=guild,
            game_name=game_name,
            category_name=category_name
        )
    
    async def create_project_channel(
        self, 
        guild: nextcord.Guild, 
        project_name: str,
        description: str = None,
        category_name: str = "PROJECTS"
    ) -> Optional[nextcord.TextChannel]:
        """Create a project channel"""
        if not self.channel_factory:
            logger.error("Channel factory not initialized")
            return None
        
        logger.info(f"Creating project channel for: {project_name}")
        return await self.channel_factory.create_project_channel(
            guild=guild,
            project_name=project_name,
            description=description,
            category_name=category_name
        )

    async def cleanup(self):
        """Cleanup resources used by the channel workflow"""
        logger.info("Cleaning up channel workflow resources")
        # Reset the objects
        self.channel_repository = None
        self.channel_setup_service = None
