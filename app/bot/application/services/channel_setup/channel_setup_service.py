"""Service for setting up and managing Discord channels."""
from typing import Dict, Any, List, Optional
import nextcord

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class ChannelSetupService:
    """Service for managing Discord server channels."""
    
    def __init__(self, bot):
        self.bot = bot
        self.initialized = False
        self.default_channels = {
            "Information": [
                "welcome", 
                "announcements"
            ],
            "General": [
                "general-chat", 
                "off-topic"
            ],
            "Bot Commands": [
                "bot-control", 
                "commands"
            ],
            "Administration": [
                "admin-chat", 
                "logs", 
                "monitoring", 
                "alerts"
            ],
            "Homelab": [
                "projects",
                "services",
                "infrastructure",
                "server-management",
                "backups"
            ]
        }
        
    async def initialize(self):
        """Initialize the channel setup service."""
        self.initialized = True
        logger.info("Channel setup service initialized")
        return True
        
    async def setup_default_channels(self, guild):
        """Set up default channels in a guild."""
        created_channels = []
        
        # First, ensure categories exist
        category_workflow = self.bot.get_workflow('category')
        if not category_workflow:
            logger.error("Category workflow not available")
            return created_channels
            
        for category_name, channel_names in self.default_channels.items():
            # Get or create category
            category = await category_workflow.get_or_create_category(guild, category_name)
            
            if not category:
                logger.error(f"Failed to create category: {category_name}")
                continue
                
            # Create channels in this category
            for channel_name in channel_names:
                # Check if channel exists
                existing = None
                for channel in guild.text_channels:
                    if channel.name.lower() == channel_name.lower():
                        existing = channel
                        break
                        
                if existing:
                    logger.debug(f"Channel already exists: {channel_name}")
                    created_channels.append(existing)
                else:
                    # Create channel
                    try:
                        channel = await guild.create_text_channel(
                            name=channel_name,
                            category=category
                        )
                        logger.info(f"Created channel: {channel_name}")
                        created_channels.append(channel)
                    except Exception as e:
                        logger.error(f"Error creating channel {channel_name}: {e}")
                    
        return created_channels
        
    async def create_channel(self, guild, name, category=None, **kwargs):
        """Create a channel in a guild."""
        try:
            if isinstance(category, str):
                # Get category by name
                category_obj = None
                for cat in guild.categories:
                    if cat.name.lower() == category.lower():
                        category_obj = cat
                        break
                        
                if not category_obj:
                    # Try to create the category
                    category_workflow = self.bot.get_workflow('category')
                    if category_workflow:
                        category_obj = await category_workflow.get_or_create_category(guild, category)
                    
                category = category_obj
                
            # Create the channel
            channel = await guild.create_text_channel(
                name=name,
                category=category,
                **kwargs
            )
            logger.info(f"Created channel: {name}")
            return channel
            
        except Exception as e:
            logger.error(f"Error creating channel {name}: {e}")
            return None
        
    async def delete_channel(self, channel):
        """Delete a channel."""
        try:
            await channel.delete()
            logger.info(f"Deleted channel: {channel.name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting channel {channel.name}: {e}")
            return False
            
    async def update_channel(self, channel, **kwargs):
        """Update a channel's settings."""
        try:
            await channel.edit(**kwargs)
            logger.info(f"Updated channel: {channel.name}")
            return True
        except Exception as e:
            logger.error(f"Error updating channel {channel.name}: {e}")
            return False 