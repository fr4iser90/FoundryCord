import nextcord
import logging
from typing import Dict, List, Optional, Any
from app.shared.domain.repositories.discord.channel_repository import ChannelRepository
from app.shared.domain.repositories.discord.category_repository import CategoryRepository
from app.bot.application.services.channel.channel_builder import ChannelBuilder
from app.shared.infrastructure.models.discord.entities.channel_entity import ChannelEntity
from app.shared.infrastructure.models.discord.enums.channels import ChannelType
from app.bot.application.services.category.category_setup_service import CategorySetupService
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class ChannelSetupService:
    """Service for managing Discord channel setup and synchronization"""
    
    def __init__(self, channel_repository: ChannelRepository, channel_builder: ChannelBuilder, category_service: CategorySetupService):
        """Initialize the channel setup service."""
        self.channel_repository = channel_repository
        self.channel_builder = channel_builder
        self.category_service = category_service
        self.channels_cache: Dict[str, ChannelEntity] = {}
    
    async def initialize(self):
        """Initialize the channel setup service."""
        logger.info("Initializing channel setup service")
        # The initialization is now handled in ChannelWorkflow.initialize()
        # to avoid direct ORM queries that might fail
        return True
    
    async def setup_channels(self, guild: nextcord.Guild) -> Dict[str, nextcord.abc.GuildChannel]:
        """
        Set up all channels for the guild and return a mapping of channel names to Discord channels
        """
        logger.info(f"Setting up channels for guild: {guild.name}")
        
        # First, set up categories if not already done
        category_channels = await self.category_service.setup_categories(guild)
        
        # Load all enabled channels from the database
        db_channels = await self.channel_repository.get_enabled_channels()
        for channel in db_channels:
            self.channels_cache[channel.name] = channel
        
        # Set up channels in Discord
        channel_map = await self.channel_builder.setup_all_channels(guild, category_channels)
        
        logger.info(f"Successfully set up {len(channel_map)} channels")
        return channel_map
    
    async def sync_with_discord(self, guild: nextcord.Guild) -> None:
        """
        Synchronize database channels with existing Discord channels
        """
        logger.info(f"Syncing channels with Discord for guild: {guild.name}")
        await self.channel_builder.sync_channels(guild)
        logger.info("Channel synchronization completed")
    
    def get_channel_by_name(self, name: str) -> Optional[ChannelEntity]:
        """
        Get a channel model by name from cache or database
        """
        if name in self.channels_cache:
            return self.channels_cache[name]
        
        # Search through all channels with this name
        # (this is less precise, as channels in different categories can have the same name)
        all_channels = self.channel_repository.get_all_channels()
        matching_channels = [c for c in all_channels if c.name == name]
        
        if matching_channels:
            channel = matching_channels[0]  # Just take the first one
            self.channels_cache[name] = channel
            return channel
        
        return None
    
    def get_channels_by_type(self, channel_type: ChannelType) -> List[ChannelEntity]:
        """
        Get all channels of a specific type
        """
        return self.channel_repository.get_channels_by_type(channel_type.value)
    
    def get_channels_by_category(self, category_name: str) -> List[ChannelEntity]:
        """
        Get all channels in a specific category
        """
        category = self.category_service.get_category_by_name(category_name)
        if not category:
            return []
        
        return self.channel_repository.get_channels_by_category_id(category.id)
    
    def refresh_cache(self) -> None:
        """
        Refresh the channels cache
        """
        self.channels_cache.clear()
        channels = self.channel_repository.get_all_channels()
        for channel in channels:
            self.channels_cache[channel.name] = channel
    
    async def create_text_channel(self, guild: nextcord.Guild, name: str, category_name: str, 
                               topic: str = None, position: int = 0) -> Optional[nextcord.TextChannel]:
        """
        Helper method to create a text channel with default settings
        """
        category = self.category_service.get_category_by_name(category_name)
        if not category:
            logger.error(f"Category not found: {category_name}")
            return None
        
        # Create a simple channel model
        channel_model = ChannelEntity(
            name=name,
            category_id=category.id,
            category_discord_id=category.discord_id,
            type=ChannelType.TEXT,
            position=position,
            topic=topic
        )
        
        # Save to DB first
        saved_channel = self.channel_repository.save_channel(channel_model)
        
        # Create in Discord
        discord_channel = await self.channel_builder.create_channel(guild, saved_channel)
        return discord_channel
    
    async def create_voice_channel(self, guild: nextcord.Guild, name: str, category_name: str, 
                                position: int = 0) -> Optional[discord.VoiceChannel]:
        """
        Helper method to create a voice channel with default settings
        """
        category = self.category_service.get_category_by_name(category_name)
        if not category:
            logger.error(f"Category not found: {category_name}")
            return None
        
        # Create a simple channel model
        channel_model = ChannelEntity(
            name=name,
            category_id=category.id,
            category_discord_id=category.discord_id,
            type=ChannelType.VOICE,
            position=position
        )
        
        # Save to DB first
        saved_channel = self.channel_repository.save_channel(channel_model)
        
        # Create in Discord
        discord_channel = await self.channel_builder.create_channel(guild, saved_channel)
        return discord_channel 