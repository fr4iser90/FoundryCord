import nextcord
from typing import Optional, Callable, Dict, Any
from infrastructure.logging import logger
from .base_view import BaseView
from ..buttons import RefreshButton

class MonitoringView(BaseView):
    """View for system monitoring dashboard"""
    
    def __init__(
        self,
        timeout: Optional[int] = None
    ):
        super().__init__(timeout=timeout)
    
    def create(self):
        """Create the view with all monitoring components"""
        # Refresh button
        refresh_button = RefreshButton(
            callback=lambda i: self._handle_callback(i, "refresh"),
            label="Aktualisieren"
        )
        self.add_item(refresh_button)
        
        # System details button
        system_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="System Details",
            emoji="🖥️",
            custom_id="monitoring_system",
            row=0
        )
        system_button.callback = lambda i: self._handle_callback(i, "system")
        self.add_item(system_button)
        
        # Services button
        services_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="Services",
            emoji="🔌",
            custom_id="monitoring_services",
            row=0
        )
        services_button.callback = lambda i: self._handle_callback(i, "services") 
        self.add_item(services_button)
        
        # Game servers button
        games_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="Game Servers",
            emoji="🎮",
            custom_id="monitoring_games",
            row=1
        )
        games_button.callback = lambda i: self._handle_callback(i, "games")
        self.add_item(games_button)
        
        return self
