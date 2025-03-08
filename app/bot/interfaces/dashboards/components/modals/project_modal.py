from typing import Optional
import nextcord
from infrastructure.logging import logger
from .base_modal import BaseModal

class ProjectModal(BaseModal):
    """Modal for project creation/editing"""
    
    def __init__(self, title: str = "Neues Projekt"):
        super().__init__(title=title)
        
        self.name = nextcord.ui.TextInput(
            label="Projektname",
            placeholder="Name des Projekts",
            min_length=3,
            max_length=100,
            required=True
        )
        self.add_item(self.name)
        
        self.description = nextcord.ui.TextInput(
            label="Beschreibung",
            placeholder="Projektbeschreibung",
            style=nextcord.TextInputStyle.paragraph,
            required=False
        )
        self.add_item(self.description)
        
        self.priority = nextcord.ui.TextInput(
            label="Priorität",
            placeholder="high/medium/low",
            min_length=3,
            max_length=6,
            required=True
        )
        self.add_item(self.priority)

    async def handle_submit(self, interaction: nextcord.Interaction):
        """Handle form submission"""
        await interaction.response.defer()