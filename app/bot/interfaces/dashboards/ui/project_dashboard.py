from typing import Dict, List, Optional, Any
import nextcord
from datetime import datetime
from infrastructure.logging import logger
from infrastructure.database.models.models import Project

# Importieren Sie die vorhandenen Komponenten
from interfaces.dashboards.components.buttons.project_buttons import ProjectActionButtons
from interfaces.dashboards.components.buttons.project_task_buttons import TaskActionButtons
from interfaces.dashboards.components.modals.project_modal import ProjectModal
from interfaces.dashboards.components.modals.project_task_modal import TaskModal
from interfaces.dashboards.components.views.project_dashboard_view import ProjectDashboardView
from interfaces.dashboards.components.views.project_details_view import ProjectDetailsView
from interfaces.dashboards.components.views.project_task_list_view import TaskListView
from interfaces.dashboards.components.views.project_thread_view import ProjectThreadView
from interfaces.dashboards.components.views.view_confirmation import ConfirmationView
from interfaces.dashboards.components.views.status_select_view import StatusSelectView

class ProjectDashboardUI:
    def __init__(self, bot):
        self.bot = bot
        self.service = None
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
    
    def set_service(self, service):
        """Dependency Injection for the service"""
        self.service = service
        logger.debug("Service injected into ProjectDashboardUI")
    
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
    
    async def create_dashboard_view(self, dashboard=None) -> nextcord.ui.View:
        """Creates the view for the dashboard with proper row management"""
        # Verwenden Sie die importierte ProjectDashboardView-Klasse ohne Parameter
        view = ProjectDashboardView()
        
        # Callbacks registrieren
        view.set_callback("refresh", lambda i: self.on_refresh(i))
        view.set_callback("new_project", lambda i: self.on_new_project(i))
        
        # View erstellen
        view.create()
        
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
    
    def create_project_actions_view(self, project):
        """Erstellt die View mit den Buttons für die Projektdetails"""
        view = nextcord.ui.View(timeout=60)
        
        # Buttons mit ProjectActionButtons erstellen
        buttons = ProjectActionButtons(project.id, self).create_project_buttons()
        
        # Buttons zur View hinzufügen
        for button in buttons:
            view.add_item(button)
        
        return view
    
    def create_new_project_modal(self):
        """Erstellt ein Modal für neue Projekte"""
        return ProjectModal()
    
    def create_edit_project_modal(self, project):
        """Erstellt ein Modal zum Bearbeiten von Projekten"""
        return ProjectModal(project)
    
    def create_status_select_view(self, project, on_status_select):
        """Erstellt eine View mit einem Status-Dropdown"""
        view = StatusSelectView(project, self.status_emojis, self.status_names)
        view.select.callback = on_status_select
        return view
    
    def create_delete_confirm_view(self, on_confirm, on_cancel):
        """Erstellt eine View zur Bestätigung des Löschens"""
        view = ConfirmationView(title="Projekt löschen")
        # Die Callbacks sind bereits in der ConfirmationView definiert
        return view
    
    def create_project_field(self, project) -> str:
        """Creates a formatted field for a project with thread link"""
        priority_emoji = ""
        if hasattr(project, 'priority') and project.priority:
            priority_emoji = self.priority_emojis.get(project.priority, '')
        
        # Format due date if available
        due_date = ""
        if hasattr(project, 'due_date') and project.due_date:
            due_date = f" | Fällig: {project.due_date.strftime('%d.%m.%Y')}"
        
        # Create thread link if thread_id is available
        thread_link = ""
        if hasattr(project, 'thread_id') and project.thread_id:
            thread_link = f" | [Zum Projekt](https://discord.com/channels/{self.bot.guild_id}/{project.thread_id})"
        
        return f"{priority_emoji} **{project.name}**{due_date}{thread_link}"
    
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

    async def setup(self):
        """Initialisiert das Dashboard"""
        try:
            # Channel aus der Config holen
            from infrastructure.config.channel_config import ChannelConfig
            channel_id = await ChannelConfig.get_channel_id('projects')
            self.channel = self.bot.get_channel(channel_id)
            
            if not self.channel:
                logger.error("Project channel not found")
                return
            
            # Dashboard anzeigen
            projects_by_status = await self.service.get_projects_by_status()
            embed = self.create_dashboard_embed(projects_by_status)
            view = await self.create_dashboard_view()
            await self.channel.send(embed=embed, view=view)
            logger.info("Project Dashboard setup completed")
            
        except Exception as e:
            logger.error(f"Error in Project Dashboard setup: {e}")
            raise

    async def on_new_project(self, interaction: nextcord.Interaction):
        """Handler für den Neues-Projekt-Button"""
        modal = self.create_new_project_modal()
        modal.callback = self.handle_new_project_submit
        await interaction.response.send_modal(modal)

    async def handle_new_project_submit(self, interaction: nextcord.Interaction, data: Dict[str, Any]):
        """Handles the submission of the new project modal"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Parse due date if provided
            due_date = None
            if data.get('due_date'):
                try:
                    due_date = datetime.strptime(data['due_date'], "%d.%m.%Y")
                except ValueError:
                    await interaction.followup.send("Ungültiges Datumsformat! Bitte DD.MM.YYYY verwenden.", ephemeral=True)
                    return
            
            # Create new project
            project = await self.service.create_project(
                name=data.get('name', 'Neues Projekt'),
                description=data.get('description', ''),
                status=data.get('status', 'planning'),
                due_date=due_date,
                priority=data.get('priority'),
                user=interaction.user
            )
            
            # Get the projects channel
            channel = await self.get_projects_channel(interaction.guild)
            
            # Create thread for this project
            thread = await self.create_project_thread(project, channel)
            
            # Store thread ID in project
            await self.service.update_project(project.id, {'thread_id': thread.id})
            
            await interaction.followup.send(
                f"Projekt '{project.name}' wurde erstellt! [Zum Projekt]({thread.jump_url})", 
                ephemeral=True
            )
            
            # Refresh dashboard
            await self.refresh_dashboard(interaction)
        except Exception as e:
            logger.error(f"Error creating project: {e}", exc_info=True)
            await interaction.followup.send("Fehler beim Erstellen des Projekts.", ephemeral=True)

    async def get_projects_channel(self, guild):
        """Gets or creates the projects channel"""
        channel_factory = self.bot.component_factory.factories['channel']
        channel = await channel_factory.get_or_create_channel(
            guild=guild,
            name="projekte",
            topic="Homelab Projekte und Aufgaben",
            is_private=False
        )
        return channel

    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handler for the Refresh button"""
        await self.refresh()
        await interaction.response.send_message("Dashboard wurde aktualisiert!", ephemeral=True)

    async def refresh(self):
        """Aktualisiert das Dashboard"""
        try:
            projects_by_status = await self.service.get_projects_by_status()
            embed = self.create_dashboard_embed(projects_by_status)
            view = await self.create_dashboard_view()
            
            if hasattr(self, 'message') and self.message:
                await self.message.edit(embed=embed, view=view)
            else:
                self.message = await self.channel.send(embed=embed, view=view)
            
            logger.debug("Project dashboard refreshed")
        except Exception as e:
            logger.error(f"Error refreshing project dashboard: {e}")

    async def create_project_thread(self, project: Project, channel) -> nextcord.Thread:
        """Creates or gets a thread for a specific project"""
        # Get the thread factory
        thread_factory = self.bot.component_factory.factories['thread']
        
        # Create thread name with project ID to ensure uniqueness
        thread_name = f"project-{project.id}-{project.name[:20]}"
        
        # Create or get thread for this project
        thread = await thread_factory.get_or_create_thread(
            channel=channel,
            name=thread_name,
            auto_archive_duration=10080,  # 7 days
            reason=f"Thread for project: {project.name}"
        )
        
        # Send initial message if it's a new thread
        if not thread.last_message_id:
            embed = self.create_project_details_embed(project)
            view = await self.create_project_thread_view(project)
            await thread.send(embed=embed, view=view)
        
        return thread

    async def create_task_modal(self, project_id: int):
        """Creates a modal for adding tasks to a project"""
        from app.bot.interfaces.dashboards.components.modals.project_task_modal import TaskModal
        modal = TaskModal(title=f"Neue Aufgabe hinzufügen")
        modal.project_id = project_id  # Store project ID for reference
        return modal

    async def handle_task_submit(self, interaction: nextcord.Interaction, data: Dict[str, Any], project_id: int):
        """Handles the submission of a new task"""
        try:
            # Create task in the database
            task = await self.service.create_task(
                project_id=project_id,
                title=data.get('title', 'Neue Aufgabe'),
                description=data.get('description', ''),
                due_date=data.get('due_date'),
                assigned_to=data.get('assigned_to')
            )
            
            # Get project for reference
            project = await self.service.get_project(project_id)
            
            # Send confirmation and update thread
            await interaction.response.send_message(
                f"Aufgabe '{task.title}' wurde zum Projekt '{project.name}' hinzugefügt!",
                ephemeral=True
            )
            
            # Update thread with new task list
            await self.update_project_thread(project)
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            await interaction.response.send_message("Fehler beim Erstellen der Aufgabe.", ephemeral=True)

    async def update_project_thread(self, project: Project):
        """Updates the project thread with current information"""
        # Find the thread
        thread_name = f"project-{project.id}-{project.name[:20]}"
        thread = None
        
        for t in self.channel.threads:
            if t.name == thread_name:
                thread = t
                break
        
        if not thread:
            logger.error(f"Thread for project {project.id} not found")
            return
        
        # Create updated embed and view
        embed = self.create_project_details_embed(project)
        view = self.create_project_view(project)
        
        # Add task list embed
        tasks_embed = await self.create_tasks_embed(project)
        
        # Find the last bot message and update it, or send new
        async for message in thread.history(limit=10):
            if message.author.id == self.bot.user.id and message.embeds:
                await message.edit(embeds=[embed, tasks_embed], view=view)
                return
        
        # If no message found, send new one
        await thread.send(embeds=[embed, tasks_embed], view=view)

    async def create_tasks_embed(self, project: Project) -> nextcord.Embed:
        """Creates an embed with the task list for a project"""
        embed = nextcord.Embed(
            title=f"📋 Aufgaben für {project.name}",
            color=0x3498db
        )
        
        if not project.tasks or len(project.tasks) == 0:
            embed.description = "Keine Aufgaben vorhanden. Füge eine neue Aufgabe hinzu!"
            return embed
        
        for i, task in enumerate(project.tasks):
            status_emoji = "⬜" if not task.completed else "✅"
            due_date = f"Fällig: {task.due_date.strftime('%d.%m.%Y')}" if task.due_date else ""
            assigned = f"Zugewiesen an: {task.assigned_to}" if task.assigned_to else ""
            
            task_text = f"{task.description}\n{due_date} {assigned}"
            embed.add_field(
                name=f"{status_emoji} {i+1}. {task.title}",
                value=task_text,
                inline=False
            )
        
        return embed

    async def create_project_thread_view(self, project):
        """Erstellt eine View für den Projekt-Thread"""
        view = ProjectThreadView(project.id)
        
        # Callbacks registrieren
        view.set_callback("add_task", self.on_task_new)
        view.set_callback("edit_project", self.on_project_edit)
        view.set_callback("change_status", self.on_change_status)
        view.set_callback("delete_project", self.on_delete_project)
        
        # View erstellen
        view.create()
        
        return view

    async def on_project_select(self, interaction: nextcord.Interaction, project_id: int):
        """Handler for when a project button is clicked"""
        try:
            # Get the project
            project = await self.service.get_project(project_id)
            if not project:
                await interaction.response.send_message("Projekt nicht gefunden!", ephemeral=True)
                return
            
            # Get or create thread for this project
            thread = await self.get_or_create_project_thread(interaction.channel, project)
            
            # Send or update project details in thread
            await self.update_project_thread(thread, project)
            
            # Send confirmation and link to thread
            await interaction.response.send_message(
                f"[Zum Projekt-Thread]({thread.jump_url})", 
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error selecting project: {e}", exc_info=True)
            await interaction.response.send_message("Fehler beim Öffnen des Projekts", ephemeral=True)

    async def get_or_create_project_thread(self, channel, project):
        """Gets or creates a thread for a project"""
        thread_factory = self.bot.component_factory.factories['thread']
        
        # Create thread name with project ID to ensure uniqueness
        thread_name = f"project-{project.id}-{project.name[:20]}"
        
        # Get or create thread
        thread = await thread_factory.get_or_create_thread(
            channel=channel,
            name=thread_name,
            auto_archive_duration=10080  # 7 days
        )
        
        return thread

    def create_task_actions_view(self, project_id, task_id):
        """Erstellt die View mit den Buttons für die Task-Aktionen"""
        view = nextcord.ui.View(timeout=60)
        
        # Buttons mit TaskActionButtons erstellen
        buttons = TaskActionButtons(task_id, project_id, self).create_task_buttons()
        
        # Buttons zur View hinzufügen
        for button in buttons:
            view.add_item(button)
        
        return view

    async def on_project_edit(self, interaction: nextcord.Interaction, project_id: int):
        """Handler für den Edit-Button"""
        try:
            project = await self.service.get_project(project_id)
            if not project:
                await interaction.response.send_message("Projekt nicht gefunden!", ephemeral=True)
                return
            
            modal = self.create_edit_project_modal(project)
            modal.callback = lambda i: self.handle_edit_project_submit(i, project_id)
            await interaction.response.send_modal(modal)
        except Exception as e:
            logger.error(f"Error editing project: {e}", exc_info=True)
            await interaction.response.send_message("Fehler beim Bearbeiten des Projekts", ephemeral=True)
