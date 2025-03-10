import nextcord
from typing import Optional, Callable, Dict, Any
from infrastructure.logging import logger
from interfaces.dashboards.components.common.views import BaseView


class BotInfoView(BaseView):
    """View for displaying detailed bot information and features"""
    
    def __init__(
        self,
        bot_name: str = "HomeLab Bot",
        bot_version: str = "1.0.0",
        timeout: Optional[int] = None
    ):
        super().__init__(timeout=timeout)
        self.bot_name = bot_name
        self.bot_version = bot_version
        self._callbacks = {}  # Initialize the callbacks dictionary
        
    def create(self):
        """Create the view with bot info components"""
        # System features button
        system_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="System Features",
            emoji="🖥️",
            custom_id="system_features",
            row=0
        )
        system_button.callback = lambda i: self._handle_callback(i, "system_features")
        self.add_item(system_button)
        
        # Dashboard features button
        dashboard_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Dashboards",
            emoji="📊",
            custom_id="dashboard_features",
            row=0
        )
        dashboard_button.callback = lambda i: self._handle_callback(i, "dashboard_features")
        self.add_item(dashboard_button)
        
        # Game server features button
        gameserver_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Game Servers",
            emoji="🎮",
            custom_id="gameserver_features",
            row=0
        )
        gameserver_button.callback = lambda i: self._handle_callback(i, "gameserver_features")
        self.add_item(gameserver_button)
        
        # Project features button
        project_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Projects",
            emoji="📋",
            custom_id="project_features",
            row=1
        )
        project_button.callback = lambda i: self._handle_callback(i, "project_features")
        self.add_item(project_button)
        
        # Security features button
        security_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Security",
            emoji="🔒",
            custom_id="security_features",
            row=1
        )
        security_button.callback = lambda i: self._handle_callback(i, "security_features")
        self.add_item(security_button)
        
        # Close button
        close_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.danger,
            label="Close",
            emoji="✖️",
            custom_id="close_bot_info",
            row=2
        )
        close_button.callback = lambda i: self._handle_callback(i, "close_info")
        self.add_item(close_button)
        
        return self
    
    def set_callback(self, button_id: str, callback: Callable):
        """Set a callback function for a specific button"""
        self._callbacks[button_id] = callback
        return self
        
    async def _handle_callback(self, interaction: nextcord.Interaction, button_id: str):
        """Handle button callbacks"""
        if button_id in self._callbacks:
            await self._callbacks[button_id](interaction)
        else:
            logger.warning(f"No callback registered for button {button_id}")
            await interaction.response.send_message("This button doesn't have functionality yet.", ephemeral=True)
