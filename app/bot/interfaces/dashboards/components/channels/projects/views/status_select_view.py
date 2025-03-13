import nextcord
from app.shared.logging import logger
from app.bot.interfaces.dashboards.components.common.views import BaseView

class StatusSelectView(BaseView):
    def __init__(self, project, status_emojis, status_names):
        super().__init__(timeout=60)
        self.project = project
        
        # Status-Dropdown
        self.select = nextcord.ui.Select(
            placeholder="Neuen Status wählen",
            min_values=1,
            max_values=1,
            options=[
                nextcord.SelectOption(
                    label=status_names.get("planning", "Planung"),
                    emoji=status_emojis.get("planning", "🔵"),
                    value="planning",
                    default="planning" == getattr(project, 'status', 'planning')
                ),
                nextcord.SelectOption(
                    label=status_names.get("in_progress", "In Bearbeitung"),
                    emoji=status_emojis.get("in_progress", "🟡"),
                    value="in_progress",
                    default="in_progress" == getattr(project, 'status', 'planning')
                ),
                nextcord.SelectOption(
                    label=status_names.get("completed", "Abgeschlossen"),
                    emoji=status_emojis.get("completed", "🟢"),
                    value="completed",
                    default="completed" == getattr(project, 'status', 'planning')
                ),
                nextcord.SelectOption(
                    label=status_names.get("on_hold", "Pausiert"),
                    emoji=status_emojis.get("on_hold", "🟠"),
                    value="on_hold",
                    default="on_hold" == getattr(project, 'status', 'planning')
                ),
                nextcord.SelectOption(
                    label=status_names.get("cancelled", "Abgebrochen"),
                    emoji=status_emojis.get("cancelled", "🔴"),
                    value="cancelled",
                    default="cancelled" == getattr(project, 'status', 'planning')
                ),
            ]
        )
        self.add_item(self.select)