"""Refresh button component for dashboards."""
from typing import Dict, Any, Optional, Callable, Awaitable
import nextcord
import asyncio

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from .base_component import DashboardComponent

class RefreshButtonComponent(DashboardComponent):
    """Button to refresh dashboard data."""
    
    async def render_to_embed(self, embed: nextcord.Embed, data: Any, config: Dict[str, Any]) -> None:
        """Refresh buttons don't render to embeds."""
        pass
    
    async def create_ui_component(self, view: nextcord.ui.View, data: Any, 
                                 config: Dict[str, Any], dashboard_id: str) -> Optional[nextcord.ui.Button]:
        """Create refresh button UI component."""
        try:
            # Extract configuration
            label = config.get('label', 'Refresh')
            emoji = config.get('emoji', '🔄')
            style_name = config.get('style', 'secondary')
            style = getattr(nextcord.ButtonStyle, style_name, nextcord.ButtonStyle.secondary)
            row = config.get('row', 0)
            
            # Create button
            button = RefreshButton(
                emoji=emoji,
                label=label,
                style=style,
                row=row,
                dashboard_id=dashboard_id
            )
            
            return button
            
        except Exception as e:
            logger.error(f"Error creating refresh button: {e}")
            return None
    
    async def on_interaction(self, interaction: nextcord.Interaction, data: Any,
                           config: Dict[str, Any], dashboard_id: str) -> None:
        """Handle refresh button interaction."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get dashboard controller
            dashboard_manager = interaction.client.dashboard_manager
            controller = await dashboard_manager.get_dashboard_controller(dashboard_id)
            
            if controller:
                # Call refresh on controller
                await controller.refresh_data()
                await controller.display_dashboard()
                
                await interaction.followup.send("Dashboard refreshed!", ephemeral=True)
            else:
                await interaction.followup.send("Could not find dashboard controller.", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error handling refresh button interaction: {e}")
            await interaction.followup.send(f"Error refreshing dashboard: {str(e)}", ephemeral=True)

class RefreshButton(nextcord.ui.Button):
    """Refresh button UI element."""
    
    def __init__(self, dashboard_id: str, **kwargs):
        super().__init__(**kwargs)
        self.dashboard_id = dashboard_id
        
    async def callback(self, interaction: nextcord.Interaction):
        """Handle button click."""
        component = RefreshButtonComponent(interaction.client, {"id": f"refresh_{self.dashboard_id}"})
        await component.on_interaction(interaction, None, {}, self.dashboard_id) 