from typing import Dict, List, Optional, Any
import nextcord
from datetime import datetime
from infrastructure.logging import logger
from infrastructure.database.models.models import Project
from interfaces.dashboards.components.buttons.project_buttons import ProjectActionButtons
from interfaces.dashboards.components.modals.project_modal import ProjectModal
from interfaces.dashboards.components.modals.task_modal import TaskModal

class ProjectDashboardUI:
    def __init__(self, bot):
        self.bot = bot
        self.status_emojis = {
            "planning": "🔵",
            "in_progress": "🟡",
            "completed": "🟢",
            "on_hold": "🟠",
            "cancelled": "🔴"
        }
        self.status_names = {
            "planning": "Planung",
            "in_progress": "In Bearbeitung",
            "completed": "Abgeschlossen",
            "on_hold": "Pausiert",
            "cancelled": "Abgebrochen"
        }
        self.priority_emojis = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
    
    def create_dashboard_embed(self, projects_by_status: Dict[str, List]) -> nextcord.Embed:
        """Erstellt das Embed für das Project Dashboard"""
        embed = nextcord.Embed(
            title="📊 Project Dashboard",
            description="Übersicht aller aktuellen Projekte im Homelab",
            color=0x3498db,
            timestamp=datetime.now()
        )
        
        # Felder für jeden Status erstellen
        for status, status_projects in projects_by_status.items():
            if not status_projects:
                continue  # Überspringe leere Status
            
            status_text = ""
            for project in status_projects:
                status_text += self.create_project_field(project)
                status_text += "\n"  # Abstand zwischen Projekten
            
            if status_text:
                status_emoji = self.status_emojis.get(status, "⚪")
                status_name = self.status_names.get(status, status.capitalize())
                embed.add_field(
                    name=f"{status_emoji} {status_name}",
                    value=status_text,
                    inline=False
                )
        
        if not any(len(projects) > 0 for projects in projects_by_status.values()):
            embed.add_field(
                name="Keine Projekte",
                value="Es wurden noch keine Projekte angelegt. Klicke auf 'Neues Projekt', um zu beginnen.",
                inline=False
            )
        
        embed.set_footer(text="Letztes Update")
        return embed
    
    async def create_dashboard_view(self, dashboard) -> nextcord.ui.View:
        """Erstellt die View für das Dashboard"""
        view = nextcord.ui.View(timeout=None)
        
        # Hauptbuttons hinzufügen
        buttons = ProjectActionButtons(0, dashboard).create_main_buttons()
        for button in buttons:
            view.add_item(button)
        
        # Projekt-Buttons für jedes Projekt
        projects = await dashboard.service.get_all_projects()
        for project in projects:
            project_buttons = ProjectActionButtons(project.id, dashboard).create_project_buttons()
            for button in project_buttons:
                view.add_item(button)
        
        return view
    
    def create_project_details_embed(self, project):
        """Erstellt ein Embed mit den Projektdetails"""
        status = getattr(project, 'status', 'planning')
        status_emoji = self.status_emojis.get(status, "⚪")
        status_name = self.status_names.get(status, status.capitalize())
        
        embed = nextcord.Embed(
            title=f"{status_emoji} {project.name}",
            description=project.description,
            color=0x3498db,
            timestamp=datetime.now()
        )
        
        # Metadaten
        embed.add_field(name="Status", value=status_name, inline=True)
        
        if hasattr(project, 'created_at') and project.created_at:
            embed.add_field(
                name="Erstellt am", 
                value=project.created_at.strftime("%d.%m.%Y"), 
                inline=True
            )
        
        if hasattr(project, 'due_date') and project.due_date:
            embed.add_field(
                name="Fällig am", 
                value=project.due_date.strftime("%d.%m.%Y"), 
                inline=True
            )
        
        if hasattr(project, 'priority') and project.priority:
            priority_emoji = self.priority_emojis.get(project.priority, '⚪')
            
            embed.add_field(
                name="Priorität", 
                value=f"{priority_emoji} {project.priority.capitalize()}", 
                inline=True
            )
        
        if hasattr(project, 'created_by') and project.created_by:
            embed.add_field(
                name="Erstellt von", 
                value=project.created_by, 
                inline=True
            )
        
        return embed
    
    def create_project_actions_view(self, on_edit, on_status_change, on_delete):
        """Erstellt die View mit den Buttons für die Projektdetails"""
        view = nextcord.ui.View(timeout=60)  # 1 Minute Timeout
        
        # Edit Button
        edit_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Bearbeiten",
            emoji="✏️",
            row=0
        )
        edit_button.callback = on_edit
        view.add_item(edit_button)
        
        # Status Button
        status_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="Status ändern",
            emoji="🔄",
            row=0
        )
        status_button.callback = on_status_change
        view.add_item(status_button)
        
        # Delete Button
        delete_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.danger,
            label="Löschen",
            emoji="🗑️",
            row=0
        )
        delete_button.callback = on_delete
        view.add_item(delete_button)
        
        return view
    
    def create_new_project_modal(self):
        """Erstellt ein Modal für neue Projekte"""
        return NewProjectModal()
    
    def create_edit_project_modal(self, project):
        """Erstellt ein Modal zum Bearbeiten von Projekten"""
        return EditProjectModal(project)
    
    def create_status_select_view(self, project, on_status_select):
        """Erstellt eine View mit einem Status-Dropdown"""
        view = StatusSelectView(project, self.status_emojis, self.status_names)
        view.select.callback = on_status_select
        return view
    
    def create_delete_confirm_view(self, on_confirm, on_cancel):
        """Erstellt eine View zur Bestätigung des Löschens"""
        view = nextcord.ui.View(timeout=60)
        
        # Confirm Button
        confirm_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.danger,
            label="Ja, löschen",
            row=0
        )
        confirm_button.callback = on_confirm
        view.add_item(confirm_button)
        
        # Cancel Button
        cancel_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="Abbrechen",
            row=0
        )
        cancel_button.callback = on_cancel
        view.add_item(cancel_button)
        
        return view
    
    def create_project_field(self, project: Project) -> str:
        """Erstellt ein formatiertes Feld für ein einzelnes Projekt"""
        status_emoji = self.status_emojis.get(project.status, "⚪")
        priority_emoji = self.priority_emojis.get(project.priority, "⚪")
        
        field = f"{status_emoji} **{project.name}** {priority_emoji}\n"
        field += f"└ {project.description[:50]}...\n" if len(project.description) > 50 else f"└ {project.description}\n"
        field += f"└ Tasks: {len(project.tasks)} | "
        field += "[Bearbeiten] [Tasks] [Status]"  # Diese werden zu Buttons/Dropdowns
        
        return field
    
    def create_project_view(self, project: Project) -> nextcord.ui.View:
        """Erstellt eine View für ein einzelnes Projekt"""
        view = nextcord.ui.View(timeout=None)
        
        # Edit Button
        edit_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="Bearbeiten",
            emoji="✏️",
            custom_id=f"edit_project_{project.id}"
        )
        
        # Add Task Button
        task_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.success,
            label="Task hinzufügen",
            emoji="📋",
            custom_id=f"add_task_{project.id}"
        )
        
        # Complete Button
        complete_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Abschließen",
            emoji="✅",
            custom_id=f"complete_project_{project.id}"
        )
        
        # Delete Button
        delete_btn = nextcord.ui.Button(
            style=nextcord.ButtonStyle.danger,
            label="Löschen",
            emoji="🗑️",
            custom_id=f"delete_project_{project.id}"
        )
        
        view.add_item(edit_btn)
        view.add_item(task_btn)
        view.add_item(complete_btn)
        view.add_item(delete_btn)
        
        return view


class NewProjectModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Neues Projekt erstellen")
        
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
            placeholder="Worum geht es in diesem Projekt?",
            style=nextcord.TextInputStyle.paragraph,
            max_length=1000,
            required=True
        )
        self.add_item(self.description)
        
        self.due_date = nextcord.ui.TextInput(
            label="Fälligkeitsdatum (DD.MM.YYYY)",
            placeholder="z.B. 01.12.2025",
            required=False
        )
        self.add_item(self.due_date)
        
        self.priority = nextcord.ui.TextInput(
            label="Priorität",
            placeholder="high, medium oder low",
            required=False
        )
        self.add_item(self.priority)

    async def callback(self, interaction: nextcord.Interaction):
        """Handler für das Modal-Submit"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Get service from bot
            dashboard_service = interaction.client.get_cog('ProjectDashboardService')
            if not dashboard_service:
                logger.error("ProjectDashboardService not found as Cog")
                dashboard_service = getattr(interaction.client, 'project_dashboard_service', None)
                if not dashboard_service:
                    await interaction.followup.send("Fehler: Dashboard Service nicht gefunden!", ephemeral=True)
                    return

            # Parse due date if provided
            due_date = None
            if self.due_date.value:
                try:
                    due_date = datetime.strptime(self.due_date.value, "%d.%m.%Y")
                except ValueError:
                    await interaction.followup.send("Ungültiges Datumsformat! Bitte DD.MM.YYYY verwenden.", ephemeral=True)
                    return

            # Create project mit User-Objekt
            await dashboard_service.create_project(
                name=self.name.value,
                description=self.description.value,
                user=interaction.user,  # Das komplette User-Objekt übergeben
                due_date=due_date,
                priority=self.priority.value if self.priority.value else None
            )

            # Refresh dashboard
            dashboard = interaction.client.get_cog('ProjectDashboard')
            if dashboard:
                await dashboard.refresh_dashboard()

            await interaction.followup.send("Projekt erfolgreich erstellt!", ephemeral=True)

        except Exception as e:
            logger.error(f"Error in modal callback: {e}", exc_info=True)
            await interaction.followup.send("Ein Fehler ist aufgetreten!", ephemeral=True)


class EditProjectModal(nextcord.ui.Modal):
    def __init__(self, project):
        super().__init__(title=f"Projekt bearbeiten: {project.name[:20]}")
        self.project = project
        
        self.name = nextcord.ui.TextInput(
            label="Projektname",
            placeholder="Name des Projekts",
            min_length=3,
            max_length=100,
            required=True,
            default_value=project.name
        )
        self.add_item(self.name)
        
        self.description = nextcord.ui.TextInput(
            label="Beschreibung",
            placeholder="Worum geht es in diesem Projekt?",
            style=nextcord.TextInputStyle.paragraph,
            max_length=1000,
            required=True,
            default_value=project.description
        )
        self.add_item(self.description)
        
        due_date_value = ""
        if hasattr(project, 'due_date') and project.due_date:
            due_date_value = project.due_date.strftime("%d.%m.%Y")
            
        self.due_date = nextcord.ui.TextInput(
            label="Fälligkeitsdatum (DD.MM.YYYY)",
            placeholder="z.B. 01.12.2025",
            required=False,
            default_value=due_date_value
        )
        self.add_item(self.due_date)
        
        priority_value = ""
        if hasattr(project, 'priority') and project.priority:
            priority_value = project.priority
            
        self.priority = nextcord.ui.TextInput(
            label="Priorität",
            placeholder="high, medium oder low",
            default_value=priority_value,
            required=False
        )
        self.add_item(self.priority)


class StatusSelectView(nextcord.ui.View):
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


class ProjectDashboardView(nextcord.ui.View):
    def __init__(self, dashboard):
        super().__init__(timeout=None)  # Kein Timeout für persistente Buttons
        self.dashboard = dashboard
        
        # Refresh Button
        refresh_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="🔄 Aktualisieren",
            custom_id="refresh_dashboard"
        )
        refresh_button.callback = self.refresh_callback
        
        # Neues Projekt Button
        new_project_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="➕ Neues Projekt",
            custom_id="new_project"
        )
        new_project_button.callback = self.new_project_callback
        
        self.add_item(refresh_button)
        self.add_item(new_project_button)
    
    async def refresh_callback(self, interaction: nextcord.Interaction):
        """Callback für den Refresh-Button"""
        await self.dashboard.on_refresh(interaction)
    
    async def new_project_callback(self, interaction: nextcord.Interaction):
        """Callback für den Neues-Projekt-Button"""
        modal = NewProjectModal()
        await interaction.response.send_modal(modal)
