from typing import Dict, Optional
from nextcord import TextChannel, Guild, CategoryChannel
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.factories.discord import ChannelFactory, ThreadFactory
from app.bot.infrastructure.config.constants.channel_constants import CHANNELS
from app.bot.infrastructure.config.constants.category_constants import CATEGORY_CHANNEL_MAPPINGS, CATEGORIES
import asyncio

class ChannelSetupService:
    def __init__(self, bot):
        self.bot = bot
        self.guild: Optional[Guild] = None
        self.channel_factory = ChannelFactory(bot)
        self.thread_factory = ThreadFactory(bot)
        
    async def initialize(self):
        """Initialize service with guild"""
        if not self.bot.guilds:
            raise ValueError("Bot is not connected to any guilds")
        self.guild = self.bot.guilds[0]
        logger.info(f"Successfully connected to guild: {self.guild.name}")
        
    async def setup(self):
        """Setup all channels and their threads"""
        try:
            if not self.guild:
                await self.initialize()
            
            # Ensure we have access to the category setup service
            if not hasattr(self.bot, 'category_setup'):
                logger.error("Category setup service not available")
                raise ValueError("Category setup service must be initialized before channel setup")
                
            # First, ensure all needed categories exist
            for category_type in CATEGORY_CHANNEL_MAPPINGS.keys():
                await self.bot.category_setup.ensure_category_exists(category_type)
            
            # Now create channels in their appropriate categories
            for category_type, channel_list in CATEGORY_CHANNEL_MAPPINGS.items():
                # Get the category object
                category = await self.bot.category_setup.get_category(category_type)
                if not category:
                    logger.warning(f"Category {category_type} not found, skipping its channels")
                    continue
                    
                logger.info(f"Setting up channels for category: {category.name}")
                
                # Create channels in this category
                for channel_name in channel_list:
                    if not channel_name:  # Skip empty channel names
                        continue
                        
                    if channel_name not in CHANNELS:
                        logger.warning(f"Channel '{channel_name}' not found in CHANNELS configuration, skipping")
                        continue
                        
                    await self._setup_channel(channel_name, CHANNELS[channel_name], category)
            
            logger.info("Channel setup completed")
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            raise
            
    async def _setup_channel(self, channel_name: str, config: Dict, category: CategoryChannel):
        """Setup a single channel and its threads in the specified category"""
        try:
            logger.info(f"Setting up channel: {channel_name} in category: {category.name}")
            
            # Clean up channel configuration
            channel_config = config.copy()
            channel_config.pop('name', None)
            threads = channel_config.pop('threads', [])
            
            # Create channel with the correct category ID
            channel = await self.channel_factory.create_channel(
                guild=self.guild,
                name=channel_name,
                category_id=category.id,  # Explicitly set category ID
                **channel_config
            )
            
            # Create threads for the channel
            if channel and threads:
                for thread_config in threads:
                    thread_name = thread_config.pop('name')
                    await self.thread_factory.create_thread(
                        channel=channel,
                        name=thread_name,
                        **thread_config
                    )
                    
            # Store mapping in database via ChannelConfig
            if channel and hasattr(self.bot, 'channel_config'):
                await self.bot.channel_config.set_channel_id(channel_name, channel.id)
                
            return channel
            
        except Exception as e:
            logger.error(f"Error setting up channel {channel_name}: {e}")
            return None 