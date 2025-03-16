from typing import Dict, Callable, List
import nextcord
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.shared.infrastructure.database.models import Project

class ProjectActionButtons:
    def __init__(self, project_id: int, dashboard):
        self.project_id = project_id
        self.dashboard = dashboard

    def create_main_buttons(self) -> List[nextcord.ui.Button]:
        """Erstellt die Hauptbuttons (Neu & Refresh)"""
        buttons = []
        
        new_project_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Neues Projekt",
            emoji="📝",
            custom_id="new_project",
            row=0
        )
        new_project_btn.callback = self.dashboard.on_new_project
        buttons.append(new_project_btn)
        
        refresh_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="Aktualisieren",
            emoji="🔄",
            custom_id="refresh_dashboard",
            row=0
        )
        refresh_btn.callback = self.dashboard.on_refresh
        buttons.append(refresh_btn)
        
        return buttons

    def create_project_buttons(self) -> List[nextcord.ui.Button]:
        """Erstellt die Projekt-spezifischen Buttons"""
        buttons = []
        
        edit_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            emoji="✏️",
            custom_id=f"edit_project_{self.project_id}",
            row=1
        )
        edit_btn.callback = lambda i: self.dashboard.on_project_edit(i, self.project_id)
        buttons.append(edit_btn)
        
        task_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.success,
            emoji="📋", 
            custom_id=f"task_project_{self.project_id}",
            row=1
        )
        task_btn.callback = lambda i: self.dashboard.on_project_task(i, self.project_id)
        buttons.append(task_btn)
        
        complete_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            emoji="✅",
            custom_id=f"complete_project_{self.project_id}",
            row=2
        )
        complete_btn.callback = lambda i: self.dashboard.on_project_complete(i, self.project_id)
        buttons.append(complete_btn)
        
        delete_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.danger,
            emoji="🗑️",
            custom_id=f"delete_project_{self.project_id}",
            row=2
        )
        delete_btn.callback = lambda i: self.dashboard.on_project_delete(i, self.project_id)
        buttons.append(delete_btn)
        
        return buttons