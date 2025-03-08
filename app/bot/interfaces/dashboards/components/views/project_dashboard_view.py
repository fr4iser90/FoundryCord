import nextcord
from typing import Callable, Optional
from infrastructure.logging import logger

class ProjectDashboardView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
        self.callbacks = {}
        
    def set_callback(self, action: str, callback: Callable):
        """Set callback for a specific action"""
        self.callbacks[action] = callback
        
    async def _handle_callback(self, interaction: nextcord.Interaction, action: str):
        """Generic handler for button callbacks"""
        if action in self.callbacks:
            await self.callbacks[action](interaction)
        else:
            await interaction.response.send_message(
                f"No callback registered for action: {action}", 
                ephemeral=True
            )
    
    def create(self):
        """Create the view with all buttons"""
        # Refresh button
        refresh_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="🔄 Aktualisieren",
            custom_id="refresh_dashboard",
            row=0
        )
        refresh_button.callback = lambda i: self._handle_callback(i, "refresh")
        self.add_item(refresh_button)
        
        # New project button
        new_project_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="➕ Neues Projekt",
            custom_id="new_project",
            row=0
        )
        new_project_button.callback = lambda i: self._handle_callback(i, "new_project")
        self.add_item(new_project_button)
        
        return self

    async def new_project_callback(self, interaction: nextcord.Interaction):
        """Callback für den Neues-Projekt-Button"""
        await self.dashboard.on_new_project(interaction)