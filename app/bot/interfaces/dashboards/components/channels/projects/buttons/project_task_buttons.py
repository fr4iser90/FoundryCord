from typing import List
import nextcord
from infrastructure.logging import logger
from infrastructure.database.models.models import Task

class TaskActionButtons:
    def __init__(self, task_id: int, project_id: int, dashboard):
        self.task_id = task_id
        self.project_id = project_id
        self.dashboard = dashboard

    def create_task_buttons(self) -> List[nextcord.ui.Button]:
        """Erstellt die Task-spezifischen Buttons"""
        buttons = []
        
        edit_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            emoji="✏️",
            label="Bearbeiten",
            custom_id=f"edit_task_{self.task_id}",
            row=0
        )
        edit_btn.callback = lambda i: self.dashboard.on_task_edit(i, self.project_id, self.task_id)
        buttons.append(edit_btn)
        
        status_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            emoji="🔄",
            label="Status",
            custom_id=f"status_task_{self.task_id}",
            row=0
        )
        status_btn.callback = lambda i: self.dashboard.on_task_status(i, self.project_id, self.task_id)
        buttons.append(status_btn)
        
        delete_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.danger,
            emoji="🗑️",
            label="Löschen",
            custom_id=f"delete_task_{self.task_id}",
            row=0
        )
        delete_btn.callback = lambda i: self.dashboard.on_task_delete(i, self.project_id, self.task_id)
        buttons.append(delete_btn)
        
        return buttons