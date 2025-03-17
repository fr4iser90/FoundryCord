from .base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.config.constants.channel_constants import CHANNELS
from typing import Dict, Any, List, Optional
import nextcord

class ChannelWorkflow(BaseWorkflow):
    """Workflow for managing Discord channel operations."""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.channel_setup_service = None
        
    async def initialize(self):
        """Initialize the channel workflow."""
        try:
            # Try to get channel setup service
            try:
                channel_setup = {
                    'name': 'channel_setup',
                    'type': 'channel_setup'
                }
                self.channel_setup_service = await self.bot.lifecycle._initialize_service(channel_setup)
            except Exception as e:
                logger.error(f"Failed to initialize channel setup service: {e}")
                # Continue without the service
                
            # Verify channel integrity
            try:
                await self._verify_channel_integrity()
            except Exception as e:
                logger.error(f"Error verifying channel integrity: {e}")
                
            logger.info("Channel workflow initialized")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing channel workflow: {e}")
            return False
    
    async def _verify_channel_integrity(self):
        """Verify that required channels exist and fix if needed."""
        logger.info("Verifying channel integrity...")
        
        try:
            # Define required channels
            required_channels = [
                'welcome',
                'gamehub',
                'services',
                'infrastructure',
                'projects',
                'backups',
                'server-management',
                'logs',
                'monitoring',
                'bot-control',
                'alerts'
            ]
            
            # Try to get the guild ID
            guild_id = None
            
            # Try to get the guild ID from environment
            import os
            guild_id = os.getenv('DISCORD_GUILD_ID')
            
            if not guild_id and hasattr(self.bot, 'config'):
                # Try to get from bot config
                guild_id = getattr(self.bot.config, 'DISCORD_GUILD_ID', None)
                if callable(getattr(self.bot.config, 'get', None)):
                    guild_id = self.bot.config.get('DISCORD_GUILD_ID')
            
            if not guild_id:
                # Default to the first guild the bot is in
                guilds = self.bot.guilds
                if guilds:
                    guild_id = guilds[0].id
            
            if not guild_id:
                logger.error("Could not determine guild ID")
                return False
                
            # Get the guild
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error("Could not find guild")
                return False
                
            # Find missing channels
            existing_channels = {channel.name: channel for channel in guild.text_channels}
            missing_channels = [name for name in required_channels if name not in existing_channels]
            
            if missing_channels:
                logger.warning(f"Found {len(missing_channels)} missing channels: {missing_channels}")
                
                # Try to repair missing channels
                for channel_name in missing_channels:
                    try:
                        await self._repair_channel(guild, channel_name)
                    except Exception as e:
                        logger.error(f"Error repairing channel {channel_name}: {e}")
            else:
                logger.info("All required channels are present")
                
            return True
            
        except Exception as e:
            logger.error(f"Error verifying channel integrity: {e}")
            return False
    
    async def _repair_channel(self, guild, channel_name):
        """Repair a missing channel."""
        try:
            # Determine which category this channel should be in
            category_name = self._get_category_for_channel(channel_name)
            
            # Find or create the category
            category = None
            for cat in guild.categories:
                if cat.name.upper() == category_name.upper():
                    category = cat
                    break
                    
            if not category:
                # Create the category
                category = await guild.create_category(category_name)
                logger.info(f"Created category: {category_name}")
                
            # Create the channel in the category
            channel = await guild.create_text_channel(
                name=channel_name,
                category=category
            )
            
            logger.info(f"Successfully repaired channel {channel_name}")
            return channel
            
        except Exception as e:
            logger.error(f"Error repairing channel {channel_name}: {e}")
            return None
    
    def _get_category_for_channel(self, channel_name):
        """Determine which category a channel should belong to."""
        if channel_name in ['gamehub']:
            return "HOMELAB GAME SERVERS"
        elif channel_name in ['welcome', 'announcements']:
            return "Information"
        elif channel_name in ['logs', 'monitoring', 'alerts', 'bot-control']:
            return "Administration"
        else:
            return "HOMELAB"
    
    async def create_channel(self, guild, name, category=None, **kwargs):
        """Create a channel in a guild."""
        if self.channel_setup_service:
            return await self.channel_setup_service.create_channel(guild, name, category, **kwargs)
        else:
            # Basic implementation
            try:
                if isinstance(category, str):
                    # Get category by name
                    category_obj = None
                    for cat in guild.categories:
                        if cat.name.lower() == category.lower():
                            category_obj = cat
                            break
                    category = category_obj
                
                channel = await guild.create_text_channel(name=name, category=category, **kwargs)
                logger.info(f"Created channel: {name}")
                return channel
            except Exception as e:
                logger.error(f"Error creating channel {name}: {e}")
                return None
                
    async def cleanup(self):
        """Clean up channel workflow resources."""
        logger.info("Channel workflow cleaned up")
        return True
