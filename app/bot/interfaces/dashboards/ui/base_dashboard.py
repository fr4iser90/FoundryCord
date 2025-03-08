from typing import Optional, Dict, Any, List
import nextcord
from datetime import datetime
from infrastructure.logging import logger
from infrastructure.config.channel_config import ChannelConfig
from interfaces.dashboards.components.buttons.refresh_button import RefreshButton

class BaseDashboardUI:
    """Base class for all dashboard UIs that handles lifecycle management"""
    
    DASHBOARD_TYPE = "base"  # Override in subclasses
    TITLE_IDENTIFIER = "Dashboard"  # Text in embed title to identify this dashboard type
    
    def __init__(self, bot):
        self.bot = bot
        self.message: Optional[nextcord.Message] = None
        self.channel: Optional[nextcord.TextChannel] = None
        self.service = None
        self.initialized = False
    
    def set_service(self, service):
        """Sets the service for this UI"""
        self.service = service
        return self
    
    async def initialize(self, channel_config_key: str = None):
        """Initialize the dashboard UI"""
        try:
            if channel_config_key:
                # Get the channel ID from config
                channel_id = await ChannelConfig.get_channel_id(channel_config_key)
                
                if not channel_id:
                    logger.error(f"No {channel_config_key} channel ID found in configuration")
                    return False
                    
                self.channel = self.bot.get_channel(channel_id)
                if not self.channel:
                    logger.error(f"Could not find {channel_config_key} channel with ID {channel_id}")
                    return False
            
            # Find existing dashboard message
            await self.find_existing_dashboard()
            
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Error initializing {self.DASHBOARD_TYPE} dashboard UI: {e}")
            return False
    
    async def find_existing_dashboard(self):
        """Find an existing dashboard message to update instead of creating a new one"""
        try:
            if not self.channel:
                return
                
            # Look at recent messages in the channel
            async for message in self.channel.history(limit=10):
                # Check if message is from the bot and has the right embed title
                if message.author.id == self.bot.user.id and message.embeds:
                    for embed in message.embeds:
                        if embed.title and self.TITLE_IDENTIFIER in embed.title:
                            logger.info(f"Found existing {self.DASHBOARD_TYPE} dashboard message: {message.id}")
                            self.message = message
                            return
            
            logger.info(f"No existing {self.DASHBOARD_TYPE} dashboard message found")
        except Exception as e:
            logger.error(f"Error finding existing dashboard message: {e}")
    
    async def cleanup_old_dashboards(self, keep_count=1):
        """Clean up old dashboard messages, keeping only the most recent ones"""
        try:
            if not self.channel:
                return
                
            dashboard_messages = []
            
            # Find all dashboard messages from the bot
            async for message in self.channel.history(limit=20):
                if message.author.id == self.bot.user.id and message.embeds:
                    for embed in message.embeds:
                        if embed.title and self.TITLE_IDENTIFIER in embed.title:
                            dashboard_messages.append(message)
            
            # Sort by creation time (newest first)
            dashboard_messages.sort(key=lambda m: m.created_at, reverse=True)
            
            # Delete all but the most recent 'keep_count' messages
            if len(dashboard_messages) > keep_count:
                for message in dashboard_messages[keep_count:]:
                    try:
                        # Don't delete the message we're currently using
                        if not self.message or message.id != self.message.id:
                            await message.delete()
                            logger.debug(f"Deleted old {self.DASHBOARD_TYPE} dashboard message: {message.id}")
                    except Exception as e:
                        logger.error(f"Error deleting old dashboard message: {e}")
        except Exception as e:
            logger.error(f"Error cleaning up old dashboard messages: {e}")
    
    async def display_dashboard(self):
        """Display or update the dashboard"""
        try:
            if not self.initialized and not await self.initialize():
                return
                
            # Create the embed and view
            embed = await self.create_embed()
            view = self.create_view()
            
            # Send or update the message
            if self.message:
                await self.message.edit(embed=embed, view=view)
                logger.info(f"Updated existing {self.DASHBOARD_TYPE} dashboard message in {self.channel.name}")
            else:
                # Clean up old messages first
                await self.cleanup_old_dashboards()
                # Create new message
                self.message = await self.channel.send(embed=embed, view=view)
                logger.info(f"Created new {self.DASHBOARD_TYPE} dashboard message in {self.channel.name}")
        except Exception as e:
            logger.error(f"Error displaying {self.DASHBOARD_TYPE} dashboard: {e}")
    
    async def create_embed(self) -> nextcord.Embed:
        """Override this method in subclasses to create the dashboard embed"""
        return nextcord.Embed(
            title=f"Base {self.TITLE_IDENTIFIER}",
            description="This is a base dashboard. Override create_embed() in a subclass.",
            color=0x3498db
        )
    
    def create_view(self) -> nextcord.ui.View:
        """Create a basic view with a refresh button - override for additional buttons"""
        view = nextcord.ui.View(timeout=None)
        
        # Refresh Button
        refresh_btn = RefreshButton(callback=self.on_refresh)
        view.add_item(refresh_btn)
        
        return view
    
    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handler for the refresh button"""
        await interaction.response.defer(ephemeral=True)
        await self.display_dashboard()
        await interaction.followup.send(f"{self.DASHBOARD_TYPE.capitalize()} Dashboard wurde aktualisiert!", ephemeral=True)
