from typing import Optional
import nextcord
from infrastructure.logging import logger
from infrastructure.database.models.models import Task

class TaskModal(nextcord.ui.Modal):
    def __init__(self, project_id: int, task: Optional[Task] = None):
        super().__init__(title="Task bearbeiten" if task else "Neuer Task")
        
        self.project_id = project_id
        
        # Felder erstellen und hinzufügen
        self.title = nextcord.ui.TextInput(
            label="Titel",
            placeholder="Task-Titel",
            default_value=task.title if task else "",
            required=True
        )
        self.add_item(self.title)
        
        self.description = nextcord.ui.TextInput(
            label="Beschreibung",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Task-Beschreibung",
            default_value=task.description if task else "",
            required=False
        )
        self.add_item(self.description)
        
        self.status = nextcord.ui.TextInput(
            label="Status",
            placeholder="open, in_progress, done",
            default_value=task.status if task else "open",
            required=True
        )
        self.add_item(self.status)