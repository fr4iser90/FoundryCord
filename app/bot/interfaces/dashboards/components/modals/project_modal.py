from typing import Optional
import nextcord
from infrastructure.logging import logger
from infrastructure.database.models.models import Project

class ProjectModal(nextcord.ui.Modal):
    def __init__(self, project: Optional[Project] = None):
        super().__init__(
            title="Projekt bearbeiten" if project else "Neues Projekt"
        )
        
        # Felder erstellen und hinzufügen
        self.name = nextcord.ui.TextInput(
            label="Name",
            placeholder="Projektname",
            default_value=project.name if project else "",
            required=True
        )
        self.add_item(self.name)
        
        self.description = nextcord.ui.TextInput(
            label="Beschreibung",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Projektbeschreibung",
            default_value=project.description if project else "",
            required=True
        )
        self.add_item(self.description)
        
        self.status = nextcord.ui.TextInput(
            label="Status",
            placeholder="planning, in_progress, completed, on_hold",
            default_value=project.status if project else "planning",
            required=True
        )
        self.add_item(self.status)
        
        self.priority = nextcord.ui.TextInput(
            label="Priorität",
            placeholder="high, medium, low",
            default_value=project.priority if project else "medium",
            required=True
        )
        self.add_item(self.priority)