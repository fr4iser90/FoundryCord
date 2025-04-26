from typing import Optional, Dict, Any, List, Union
import nextcord
from datetime import datetime
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.config.channel_config import ChannelConfig
from app.bot.interfaces.dashboards.components.common.buttons.refresh_button import RefreshButton
from app.bot.interfaces.dashboards.components.common.embeds import ErrorEmbed, DashboardEmbed  # Add this import
import asyncio
import logging

logger = logging.getLogger("homelab.dashboards")

class BaseDashboardController:
    """Base controller for all dashboard types"""
    
    # Constants for inherited classes to override
    DASHBOARD_TYPE = "base"
    TITLE_IDENTIFIER = "Base Dashboard"
    
    def __init__(self, dashboard_id: str, channel_id: int, **kwargs):
        """Initialize the dashboard controller"""
        # Dashboard identification
        self.dashboard_id = dashboard_id
        self.channel_id = channel_id
        self.guild_id = kwargs.get('guild_id')
        
        # Configuration
        self.config = kwargs.get('config', {})
        self.title = kwargs.get('title', "Dashboard")
        self.description = kwargs.get('description', "")
        
        # State tracking
        self.bot = None
        self.message_id = kwargs.get('message_id', None)
        self.message = None
        self.components = {}
        self.service = None
        self.initialized = False
        self.rate_limits = {}
        
        logger.info(f"Initialized base dashboard controller for dashboard {dashboard_id}")
    
    async def initialize(self, bot):
        """Initialize the dashboard controller"""
        self.bot = bot
        
        # Load components for this dashboard if needed
        await self.load_components()
        self.initialized = True
        
        return True
    
    async def load_components(self):
        """Load components for this dashboard"""
        try:
            logger.info(f"Loading components for dashboard {self.dashboard_id}")
            
            # Get dashboard repository from bot's service factory
            if hasattr(self.bot, 'service_factory'):
                repository = self.bot.service_factory.get_service('dashboard_repository')
                if repository:
                    # Fetch components from database
                    components = await repository.get_components_for_dashboard(self.dashboard_id)
                    if components:
                        logger.info(f"Loaded {len(components)} components from database")
                        self.components = {comp.component_id: comp for comp in components}
                        return True
            
            logger.warning(f"No components found for dashboard {self.dashboard_id}")
            return False
        except Exception as e:
            logger.error(f"Error loading components: {e}")
            return False
    
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
    
    async def refresh(self, interaction: Optional[nextcord.Interaction] = None):
        """Refresh the dashboard display"""
        logger.info(f"Refreshing dashboard {self.dashboard_id}")
        # Update data
        await self.refresh_data()
        
        # Update display
        return await self.display_dashboard()
    
    async def get_channel(self) -> Optional[nextcord.TextChannel]:
        """Get the channel for this dashboard"""
        if not self.bot:
            logger.error(f"Dashboard {self.dashboard_id} has no bot reference")
            return None
            
        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                logger.warning(f"Channel {self.channel_id} not found for dashboard {self.dashboard_id}")
            return channel
        except Exception as e:
            logger.error(f"Error getting channel for dashboard {self.dashboard_id}: {str(e)}")
            return None
    
    async def display_dashboard(self):
        """Display or update the dashboard in the channel."""
        if not self.initialized:
            logger.error(f"Attempted to display uninitialized dashboard: {self.DASHBOARD_TYPE}")
            return None
            
        channel = await self.get_channel()
        if not channel:
            logger.error(f"No channel available for dashboard: {self.dashboard_id}")
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
                    self.message = await channel.send(embed=embed, view=view)
            elif self.message_id:
                try:
                    self.message = await channel.fetch_message(self.message_id)
                    await self.message.edit(embed=embed, view=view)
                except (nextcord.NotFound, nextcord.HTTPException):
                    # Message was deleted, create new one
                    self.message = await channel.send(embed=embed, view=view)
                    self.message_id = self.message.id
            else:
                # No existing message, create new one
                self.message = await channel.send(embed=embed, view=view)
                self.message_id = self.message.id
                
            return self.message
            
        except Exception as e:
            logger.error(f"Error displaying dashboard {self.dashboard_id}: {e}")
            return None
            
    def apply_standard_footer(self, embed):
        """Apply standard footer to embed."""
        embed.set_footer(text=f"HomeLab Discord Bot • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return embed
    
    async def check_rate_limit(self, interaction: nextcord.Interaction, action_type, cooldown_seconds=10):
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

