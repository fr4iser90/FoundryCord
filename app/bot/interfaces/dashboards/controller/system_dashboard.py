import discord
import nextcord
import logging
from typing import Dict, Any, Optional, List
import asyncio

from app.bot.interfaces.dashboards.controller.base_dashboard import BaseDashboardController

logger = logging.getLogger("homelab.dashboards")

class SystemDashboardController(BaseDashboardController):
    """Controller for system monitoring dashboards"""
    
    # Override constants
    DASHBOARD_TYPE = "system"
    TITLE_IDENTIFIER = "System Status"
    
    async def initialize(self, bot):
        """Initialize the system dashboard controller"""
        await super().initialize(bot)
        
        # Set up specific system dashboard components and data sources
        self.update_interval = self.config.get('update_interval', 60)  # seconds
        
        logger.info(f"Initialized system dashboard controller with update interval: {self.update_interval}s")
        return True
    
    async def load_components(self):
        """Load system-specific components"""
        await super().load_components()
        
        # Here we would load specific components for a system dashboard
        # For example: CPU usage, memory usage, disk space, etc.
        
        return True
    
    async def start_monitoring(self):
        """Start the background monitoring task"""
        # This would normally create a background task to update the dashboard
        logger.info(f"Starting monitoring for system dashboard {self.dashboard_id}")
        return True
    
    async def collect_system_metrics(self):
        """Collect system metrics for display"""
        # This would collect actual system metrics in a real implementation
        # For now, just return placeholder data
        return {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_space": 82.3,
            "uptime": "3d 12h 45m"
        }
    
    async def refresh_data(self):
        """Refresh the system data"""
        # Collect metrics and store them for rendering
        self.metrics = await self.collect_system_metrics()
        return self.metrics
    
    async def create_embed(self):
        """Create the system dashboard embed"""
        embed = nextcord.Embed(
            title=f"{self.TITLE_IDENTIFIER} Dashboard",
            description="Current system metrics",
            color=nextcord.Color.blue()
        )
        
        # Add metrics to embed if they exist
        if hasattr(self, 'metrics'):
            for key, value in self.metrics.items():
                embed.add_field(
                    name=key.replace('_', ' ').title(),
                    value=str(value),
                    inline=True
                )
                
        # Add timestamp
        self.apply_standard_footer(embed)
        
        return embed
    
    async def create_view(self):
        """Create the dashboard view with buttons"""
        view = nextcord.ui.View(timeout=None)
        
        # Add a refresh button
        refresh_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="Refresh",
            emoji="🔄",
            custom_id=f"refresh_system_{self.dashboard_id}"
        )
        
        async def refresh_callback(interaction: nextcord.Interaction):
            # Check rate limit
            if not await self.check_rate_limit(interaction, "refresh", 5):
                return
                
            await interaction.response.defer()
            await self.refresh(interaction)
            
        refresh_button.callback = refresh_callback
        view.add_item(refresh_button)
        
        return view
    
    async def refresh(self, interaction: Optional[discord.Interaction] = None):
        """Refresh the system dashboard with current metrics"""
        try:
            # Get the channel
            channel = await self.get_channel()
            if not channel:
                return False
                
            # Collect metrics
            metrics = await self.collect_system_metrics()
            
            # Create embed components
            embed = discord.Embed(
                title="System Status Dashboard",
                description="Current system metrics",
                color=discord.Color.blue()
            )
            
            # Add metrics to embed
            for key, value in metrics.items():
                embed.add_field(
                    name=key.replace('_', ' ').title(),
                    value=str(value),
                    inline=True
                )
                
            # Add timestamp
            embed.timestamp = discord.utils.utcnow()
            
            # Update or send message
            if self.message_id:
                try:
                    message = await channel.fetch_message(self.message_id)
                    await message.edit(embed=embed)
                    logger.info(f"Updated system dashboard {self.dashboard_id}")
                except discord.NotFound:
                    # Message was deleted, create a new one
                    message = await channel.send(embed=embed)
                    self.message_id = message.id
                    logger.info(f"Recreated system dashboard {self.dashboard_id}")
            else:
                # No message ID, create a new message
                message = await channel.send(embed=embed)
                self.message_id = message.id
                logger.info(f"Created new system dashboard {self.dashboard_id}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing system dashboard {self.dashboard_id}: {str(e)}")
            return False 