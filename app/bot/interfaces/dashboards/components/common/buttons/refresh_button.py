"""Refresh button component."""
import nextcord
from typing import Dict, Any

class RefreshButton(nextcord.ui.Button):
    """Button component for refreshing dashboard."""
    
    def __init__(self, custom_id: str = "refresh_dashboard", label: str = "Refresh", **kwargs):
        super().__init__(
            custom_id=custom_id,
            label=label,
            style=nextcord.ButtonStyle.secondary,
            emoji="🔄",
            **kwargs
        )
        
    async def callback(self, interaction: nextcord.Interaction):
        """Handle button interaction."""
        # This will be handled by the dashboard controller
        pass 