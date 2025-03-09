import nextcord
from datetime import datetime
from infrastructure.logging import logger
from interfaces.dashboards.components.common.views import BaseView

class ProjectDetailsView(BaseView):
    def __init__(self, project, dashboard):
        super().__init__(timeout=None)
        self.project = project
        self.dashboard = dashboard

    def create_embed(self) -> nextcord.Embed:
        """Erstellt das Detail-Embed für ein Projekt"""
        embed = nextcord.Embed(
            title=f"📋 {self.project.name}",
            description=self.project.description,
            color=0x3498db,
            timestamp=datetime.now()
        )
        
        # Metadaten
        embed.add_field(name="Status", value=self.project.status, inline=True)
        embed.add_field(name="Priorität", value=self.project.priority, inline=True)
        if self.project.due_date:
            embed.add_field(name="Fällig am", value=self.project.due_date.strftime("%d.%m.%Y"), inline=True)
        
        # Task-Statistiken
        total_tasks = len(self.project.tasks) if hasattr(self.project, 'tasks') else 0
        completed_tasks = len([t for t in self.project.tasks if t.status == "done"]) if hasattr(self.project, 'tasks') else 0
        embed.add_field(name="Tasks", value=f"{completed_tasks}/{total_tasks} erledigt", inline=True)
        
        return embed

    @nextcord.ui.button(label="Tasks anzeigen", style=nextcord.ButtonStyle.primary, emoji="📋")
    async def show_tasks(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Zeigt die Task-Liste an"""
        await self.dashboard.show_task_list(interaction, self.project.id)

    @nextcord.ui.button(label="Bearbeiten", style=nextcord.ButtonStyle.secondary, emoji="✏️")
    async def edit_project(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Öffnet das Edit-Modal"""
        await self.dashboard.on_project_edit(interaction, self.project.id)