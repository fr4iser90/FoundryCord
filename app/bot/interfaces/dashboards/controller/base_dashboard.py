from typing import Optional, Dict, Any, List, Union
import nextcord
from datetime import datetime
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.config.channel_config import ChannelConfig
from app.bot.interfaces.dashboards.components.common.buttons.refresh_button import RefreshButton
from app.bot.interfaces.dashboards.components.common.embeds import ErrorEmbed, DashboardEmbed  # Add this import
import asyncio


class BaseDashboardController:
    """Base controller for all dashboard implementations."""
    
    # Constants for inherited classes to override
    DASHBOARD_TYPE = "base"
    TITLE_IDENTIFIER = "Base Dashboard"
    
    def __init__(self, bot):
        self.bot = bot
        self.service = None
        self.title = "Dashboard"
        self.description = ""
        self.channel = None
        self.message = None
        self.initialized = False
        self.rate_limits = {}
    
    async def initialize(self):
        """Initialize the dashboard controller. Override in subclasses."""
        self.initialized = True
        return True
    
    async def set_service(self, service):
        """Set the service for this dashboard."""
        self.service = service
        return self
    
    async def set_channel(self, channel):
        """Set the channel for this dashboard."""
        self.channel = channel
        return self
    
    async def create_embed(self):
        """Create the dashboard embed. Override in subclasses."""
        embed = nextcord.Embed(
            title=self.title,
            description=self.description,
            color=0x3498db
        )
        self.apply_standard_footer(embed)
        return embed
    
    async def create_view(self):
        """Create the dashboard view with buttons. Override in subclasses."""
        return nextcord.ui.View(timeout=None)
    
    async def refresh_data(self):
        """Refresh dashboard data. Override in subclasses."""
        pass
    
    async def display_dashboard(self):
        """Display or update the dashboard in the channel."""
        if not self.initialized:
            logger.error(f"Attempted to display uninitialized dashboard: {self.DASHBOARD_TYPE}")
            return None
            
        if not self.channel:
            logger.error(f"No channel set for dashboard: {self.DASHBOARD_TYPE}")
            return None
            
        try:
            # Create embed and view
            embed = await self.create_embed()
            view = await self.create_view()
            
            # Update existing message or send new one
            if self.message:
                try:
                    await self.message.edit(embed=embed, view=view)
                except (nextcord.NotFound, nextcord.HTTPException):
                    # Message was deleted, create new one
                    self.message = await self.channel.send(embed=embed, view=view)
            else:
                # No existing message, create new one
                self.message = await self.channel.send(embed=embed, view=view)
                
            return self.message
            
        except Exception as e:
            logger.error(f"Error displaying dashboard {self.DASHBOARD_TYPE}: {e}")
            return None
            
    def apply_standard_footer(self, embed):
        """Apply standard footer to embed."""
        embed.set_footer(text=f"HomeLab Discord Bot • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return embed
    
    async def check_rate_limit(self, interaction, action_type, cooldown_seconds=10):
        """Check if an action is rate limited."""
        user_id = interaction.user.id
        current_time = datetime.now().timestamp()
        
        # Initialize user's rate limits if not exists
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = {}
            
        # Check if action is on cooldown
        last_use = self.rate_limits[user_id].get(action_type, 0)
        time_diff = current_time - last_use
        
        if time_diff < cooldown_seconds:
            # Action is rate limited
            remaining = int(cooldown_seconds - time_diff)
            await interaction.response.send_message(
                f"Please wait {remaining} seconds before using this action again.", 
                ephemeral=True
            )
            return False
            
        # Update last use time
        self.rate_limits[user_id][action_type] = current_time
        return True
    
    def create_error_embed(self, error_message, title="Error", error_code=None):
        """Create a standardized error embed."""
        embed = nextcord.Embed(
            title=f"❌ {title}",
            description=error_message,
            color=0xe74c3c
        )
        
        if error_code:
            embed.set_footer(text=f"Error Code: {error_code}")
            
        return embed
    
    async def cleanup(self):
        """Clean up resources. Override in subclasses if needed."""
        pass

