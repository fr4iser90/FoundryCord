from typing import Optional
import nextcord
from infrastructure.logging import logger
from infrastructure.database.models import Task
from interfaces.dashboards.components.common.modals import BaseModal

class TaskModal(BaseModal):
    """Modal for task creation/editing"""
    
    def __init__(self, title: str = "Neue Aufgabe"):
        super().__init__(title=title)
        
        self.title_input = nextcord.ui.TextInput(
            label="Titel",
            placeholder="Titel der Aufgabe",
            min_length=3,
            max_length=100,
            required=True
        )
        self.add_item(self.title_input)
        
        self.description = nextcord.ui.TextInput(
            label="Beschreibung",
            placeholder="Aufgabenbeschreibung",
            style=nextcord.TextInputStyle.paragraph,
            required=False
        )
        self.add_item(self.description)

    async def handle_submit(self, interaction: nextcord.Interaction):
        """Handle form submission"""
        await interaction.response.defer()