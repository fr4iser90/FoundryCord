import nextcord
from typing import Callable, Optional
from app.shared.logging import logger
from app.bot.interfaces.dashboards.components.common.views import BaseView

class ProjectThreadView(BaseView):
    def __init__(self, project_id: int):
        super().__init__(timeout=None)  # Persistent view
        self.project_id = project_id
    
    async def _handle_callback(self, interaction: nextcord.Interaction, action: str):
        """Generic handler for button callbacks with project_id"""
        try:
            if action in self.callbacks:
                await self.callbacks[action](interaction, self.project_id)
            else:
                logger.warning(f"No callback registered for action: {action}")
                await interaction.response.send_message(
                    "Diese Aktion ist nicht verfügbar",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error in view callback: {e}")
            await interaction.response.send_message(
                "Ein Fehler ist aufgetreten",
                ephemeral=True
            )
    
    def create(self):
        """Create the view with all buttons"""
        # Add task button
        add_task_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="➕ Neue Aufgabe",
            custom_id=f"add_task_{self.project_id}",
            row=0
        )
        add_task_button.callback = lambda i: self._handle_callback(i, "add_task")
        self.add_item(add_task_button)
        
        # Edit project button
        edit_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="✏️ Projekt bearbeiten",
            custom_id=f"edit_project_{self.project_id}",
            row=0
        )
        edit_button.callback = lambda i: self._handle_callback(i, "edit_project")
        self.add_item(edit_button)
        
        # Change status button
        status_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="🔄 Status ändern",
            custom_id=f"change_status_{self.project_id}",
            row=0
        )
        status_button.callback = lambda i: self._handle_callback(i, "change_status")
        self.add_item(status_button)
        
        # Delete button (in row 1 to separate it)
        delete_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.danger,
            label="🗑️ Projekt löschen",
            custom_id=f"delete_project_{self.project_id}",
            row=1
        )
        delete_button.callback = lambda i: self._handle_callback(i, "delete_project")
        self.add_item(delete_button)
        
        return self