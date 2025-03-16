import nextcord
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.interfaces.dashboards.components.common.views import BaseView

class TaskListView(BaseView):
    def __init__(self, project, dashboard):
        super().__init__(timeout=None)
        self.project = project
        self.dashboard = dashboard

    def create_embed(self) -> nextcord.Embed:
        """Erstellt das Task-Listen Embed"""
        embed = nextcord.Embed(
            title=f"📋 Tasks: {self.project.name}",
            color=0x3498db
        )
        
        # Tasks nach Status gruppieren
        tasks_by_status = {
            "open": [],
            "in_progress": [],
            "done": []
        }
        
        for task in self.project.tasks:
            tasks_by_status[task.status].append(task)
        
        # Status-Felder hinzufügen
        status_emojis = {"open": "⭕", "in_progress": "🟡", "done": "✅"}
        status_names = {"open": "Offen", "in_progress": "In Arbeit", "done": "Erledigt"}
        
        for status, tasks in tasks_by_status.items():
            if tasks:
                task_list = "\n".join([f"• {task.title}" for task in tasks])
                embed.add_field(
                    name=f"{status_emojis[status]} {status_names[status]} ({len(tasks)})",
                    value=task_list or "Keine Tasks",
                    inline=False
                )
        
        return embed

    @nextcord.ui.button(label="Neuer Task", style=nextcord.ButtonStyle.primary, emoji="➕")
    async def add_task(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Öffnet das New Task Modal"""
        await self.dashboard.on_task_new(interaction, self.project.id)

    @nextcord.ui.button(label="Zurück zum Projekt", style=nextcord.ButtonStyle.secondary, emoji="◀️")
    async def back_to_project(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Zeigt die Projekt-Details an"""
        await self.dashboard.show_project_details(interaction, self.project.id)