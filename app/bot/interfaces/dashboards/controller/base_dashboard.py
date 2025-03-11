from typing import Optional, Dict, Any, List
import nextcord
from datetime import datetime
from infrastructure.logging import logger
from infrastructure.config.channel_config import ChannelConfig
from interfaces.dashboards.components.common.buttons.refresh_button import RefreshButton

class BaseDashboardController:
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
                channel_id = await ChannelConfig.get_channel_id(channel_config_key)
                if not channel_id:
                    return False
                    
                self.channel = self.bot.get_channel(channel_id)
                if not self.channel:
                    return False
            
            # Try to recover existing message
            self.message = await self.bot.dashboard_manager.get_tracked_message(self.DASHBOARD_TYPE)
            if self.message:
                logger.info(f"Recovered existing {self.DASHBOARD_TYPE} dashboard message")
            
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Error initializing {self.DASHBOARD_TYPE} dashboard UI: {e}")
            return False
    
    async def find_existing_dashboard(self):
        """Find an existing dashboard message to update instead of creating a new one"""
        try:
            if not self.channel:
                return None
            
            # FIRST: Try to get message from dashboard manager
            if hasattr(self.bot, 'dashboard_manager'):
                self.message = await self.bot.dashboard_manager.get_tracked_message(self.DASHBOARD_TYPE)
                if self.message:
                    logger.info(f"Found existing {self.DASHBOARD_TYPE} dashboard using message reference")
                    return self.message
                    
            # SECOND: Search channel history for dashboard with same title
            async for message in self.channel.history(limit=20):
                if message.author.id == self.bot.user.id and message.embeds:
                    for embed in message.embeds:
                        if embed.title and self.TITLE_IDENTIFIER in embed.title:
                            self.message = message
                            # Track this message for future reference
                            if hasattr(self.bot, 'dashboard_manager'):
                                await self.bot.dashboard_manager.track_message(
                                    self.DASHBOARD_TYPE, message.id, self.channel.id
                                )
                            logger.info(f"Found existing {self.DASHBOARD_TYPE} dashboard by searching channel")
                            return message
            
            return None
        except Exception as e:
            logger.error(f"Error finding existing dashboard: {e}")
            return None
    
    async def cleanup_old_dashboards(self, keep_count=1):
        """Clean up old dashboard messages, keeping only the most recent ones"""
        try:
            if not self.channel:
                return
                
            dashboard_messages = []
            
            # Find all dashboard messages from the bot that match this dashboard type
            async for message in self.channel.history(limit=20):
                if message.author.id == self.bot.user.id and message.embeds:
                    for embed in message.embeds:
                        if embed.title and self.TITLE_IDENTIFIER in embed.title:
                            dashboard_messages.append(message)
                            break  # No need to check more embeds for this message
            
            # Log how many found
            if dashboard_messages:
                logger.debug(f"Found {len(dashboard_messages)} {self.DASHBOARD_TYPE} dashboard messages to consider for cleanup")
                
                # Sort by creation time (newest first)
                dashboard_messages.sort(key=lambda m: m.created_at, reverse=True)
                
                # Keep track of messages being deleted
                deleted_count = 0
                
                # Delete all but the most recent 'keep_count' messages
                if len(dashboard_messages) > keep_count:
                    for message in dashboard_messages[keep_count:]:
                        try:
                            await message.delete()
                            deleted_count += 1
                            logger.debug(f"Deleted old {self.DASHBOARD_TYPE} dashboard message: {message.id}")
                        except Exception as e:
                            logger.error(f"Error deleting old dashboard message: {e}")
                
                logger.info(f"Deleted {deleted_count} old {self.DASHBOARD_TYPE} dashboard messages")
        except Exception as e:
            logger.error(f"Error cleaning up old dashboard messages: {e}")
    
    async def display_dashboard(self):
        """Display or update the dashboard"""
        try:
            if not self.initialized and not await self.initialize():
                return None
            
            # First attempt to find existing dashboard
            if not self.message:
                self.message = await self.find_existing_dashboard()
            
            # If we still don't have a message (none found or recovered)
            if not self.message:
                # Delete any existing dashboards in this channel of the same type
                try:
                    deleted = 0
                    async for message in self.channel.history(limit=10):
                        if message.author.id == self.bot.user.id and message.embeds:
                            for embed in message.embeds:
                                if embed.title and self.TITLE_IDENTIFIER in embed.title:
                                    await message.delete()
                                    deleted += 1
                                    logger.info(f"Deleted old {self.DASHBOARD_TYPE} dashboard")
                                    break
                    if deleted > 0:
                        logger.info(f"Cleaned up {deleted} old {self.DASHBOARD_TYPE} dashboards")
                except Exception as e:
                    logger.error(f"Error cleaning up old dashboards: {e}")
            
            # Create/update dashboard
            embed = await self.create_embed()
            view = self.create_view()
            
            if self.message:
                try:
                    await self.message.edit(embed=embed, view=view)
                    logger.info(f"Updated existing {self.DASHBOARD_TYPE} dashboard")
                except nextcord.NotFound:
                    self.message = await self.channel.send(embed=embed, view=view)
                    logger.info(f"Recreated {self.DASHBOARD_TYPE} dashboard")
            else:
                self.message = await self.channel.send(embed=embed, view=view)
                logger.info(f"Created new {self.DASHBOARD_TYPE} dashboard")
            
            # Track the message in database
            if self.message:
                await self.bot.dashboard_manager.track_message(
                    self.DASHBOARD_TYPE,
                    self.message.id,
                    self.channel.id
                )
            
            return self.message
        except Exception as e:
            logger.error(f"Error displaying {self.DASHBOARD_TYPE} dashboard: {e}")
            return None
    
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
        
        # Simply update the current dashboard
        await self.display_dashboard()
        
        await interaction.followup.send(
            f"{self.DASHBOARD_TYPE.capitalize()} Dashboard wurde aktualisiert!", 
            ephemeral=True
        )

    # async def setup(self):
    #     """Initialisiert das Dashboard"""
    #     try:
    #         # Channel aus der Config holen
    #         from infrastructure.config.channel_config import ChannelConfig
    #         channel_id = await ChannelConfig.get_channel_id('projects')
    #         self.channel = self.bot.get_channel(channel_id)
            
    #         if not self.channel:
    #             logger.error("Project channel not found")
    #             return
            
    #         # Initialize
    #         self.projects_data = await self.service.get_projects_by_status()
    #         self.initialized = True
            
    #         # Display dashboard with our custom implementation
    #         await self.display_dashboard()
    #         logger.info("Project Dashboard setup completed")
            
    #     except Exception as e:
    #         logger.error(f"Error in Project Dashboard setup: {e}")
    #         raise
