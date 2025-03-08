from typing import Dict, List, Optional
import nextcord
from infrastructure.logging import logger
from interfaces.dashboards.templates.project_dashboard import ProjectDashboardUI, NewProjectModal
from application.services.project_dashboard_service import ProjectDashboardService
from infrastructure.config.channel_config import ChannelConfig
from interfaces.dashboards.components.views.confirmation_view import ConfirmationView
from interfaces.dashboards.components.views.project_details_view import ProjectDetailsView
from interfaces.dashboards.components.views.task_list_view import TaskListView
from interfaces.dashboards.components.modals.project_modal import ProjectModal
from interfaces.dashboards.components.modals.task_modal import TaskModal

class ProjectDashboard:
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.dashboard_message = None
        self.ui = ProjectDashboardUI(bot)
        # Service vom Bot holen
        self.service = getattr(bot, 'project_dashboard_service', None)
        if not self.service:
            logger.error("ProjectDashboardService not found in bot instance")
        logger.debug("ProjectDashboard initialized")

    def set_service(self, service):
        """Dependency Injection für den Service"""
        self.service = service
        logger.debug("Service injected into ProjectDashboard")

    async def setup(self):
        """Initialisiert das Dashboard im Channel"""
        try:
            logger.debug("Starting ProjectDashboard.setup()")
            
            # Get channel ID from config
            channel_id = await ChannelConfig.get_channel_id('projects')
            logger.debug(f"Got channel_id: {channel_id}")
            
            if not channel_id:
                logger.error("Projects channel ID not found in config")
                return False

            # Get channel
            self.channel = self.bot.get_channel(channel_id)
            logger.debug(f"Got channel: {self.channel}")
            
            if not self.channel:
                logger.error(f"Channel not found for ID: {channel_id}")
                return False

            # Clean up old messages
            await self.clean_channel()

            # Get projects and create dashboard
            await self.refresh_dashboard()
            return True

        except Exception as e:
            logger.error(f"Failed to setup Project Dashboard: {e}", exc_info=True)
            return False

    async def clean_channel(self):
        """Löscht alte Dashboard Messages im Channel"""
        try:
            async for message in self.channel.history(limit=100):
                if message.author == self.bot.user:
                    await message.delete()
            logger.debug("Cleaned up old dashboard messages")
        except Exception as e:
            logger.error(f"Error cleaning channel: {e}")

    async def refresh_dashboard(self):
        """Aktualisiert das Dashboard"""
        try:
            projects = await self.service.get_projects_by_status()
            embed = self.ui.create_dashboard_embed(projects)
            view = await self.ui.create_dashboard_view(self)

            if self.dashboard_message:
                await self.dashboard_message.edit(embed=embed, view=view)
            else:
                self.dashboard_message = await self.channel.send(embed=embed, view=view)
            
            logger.debug("Dashboard refreshed successfully")
            return True
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {e}")
            return False

    async def on_new_project(self, interaction: nextcord.Interaction):
        """Handler für den Neues Projekt Button"""
        modal = NewProjectModal()
        await interaction.response.send_modal(modal)

    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handler für den Refresh Button"""
        try:
            await interaction.response.defer()
            success = await self.refresh_dashboard()
            if success:
                await interaction.followup.send("Dashboard wurde aktualisiert!", ephemeral=True)
            else:
                await interaction.followup.send("Fehler beim Aktualisieren des Dashboards.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in on_refresh: {e}")
            await interaction.followup.send("Ein Fehler ist aufgetreten.", ephemeral=True)

    # Projekt-Handler
    async def on_project_edit(self, interaction: nextcord.Interaction, project_id: int):
        """Handler für Projekt-Bearbeitung"""
        try:
            project = await self.service.get_project(project_id)
            if not project:
                await interaction.response.send_message("Projekt nicht gefunden!", ephemeral=True)
                return
            
            modal = ProjectModal(project)
            await interaction.response.send_modal(modal)
        except Exception as e:
            logger.error(f"Error in project edit: {e}")
            await interaction.response.send_message("Ein Fehler ist aufgetreten!", ephemeral=True)

    async def show_project_details(self, interaction: nextcord.Interaction, project_id: int):
        """Zeigt die Projekt-Details an"""
        try:
            project = await self.service.get_project(project_id)
            if not project:
                await interaction.response.send_message("Projekt nicht gefunden!", ephemeral=True)
                return
            
            view = ProjectDetailsView(project, self)
            embed = view.create_embed()
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"Error showing project details: {e}")
            await interaction.response.send_message("Ein Fehler ist aufgetreten!", ephemeral=True)

    async def on_project_delete(self, interaction: nextcord.Interaction, project_id: int):
        """Handler für Projekt-Löschung"""
        try:
            project = await self.service.get_project(project_id)
            if not project:
                await interaction.response.send_message("Projekt nicht gefunden!", ephemeral=True)
                return
            
            confirm_view = ConfirmationView(title="Projekt löschen")
            await confirm_view.send_confirmation(
                interaction,
                f"Möchtest du das Projekt **{project.name}** wirklich löschen?"
            )
            
            await confirm_view.wait()
            if confirm_view.value:
                await self.service.delete_project(project_id)
                await self.refresh_dashboard()
                await interaction.followup.send("Projekt wurde gelöscht!", ephemeral=True)
            else:
                await interaction.followup.send("Löschung abgebrochen.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in project delete: {e}")
            await interaction.followup.send("Ein Fehler ist aufgetreten!", ephemeral=True)

    # Task-Handler
    async def show_task_list(self, interaction: nextcord.Interaction, project_id: int):
        """Zeigt die Task-Liste eines Projekts"""
        try:
            project = await self.service.get_project(project_id)
            if not project:
                await interaction.response.send_message("Projekt nicht gefunden!", ephemeral=True)
                return
            
            view = TaskListView(project, self)
            embed = view.create_embed()
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"Error showing task list: {e}")
            await interaction.response.send_message("Ein Fehler ist aufgetreten!", ephemeral=True)

    async def on_task_new(self, interaction: nextcord.Interaction, project_id: int):
        """Handler für neue Tasks"""
        try:
            modal = TaskModal(project_id)
            await interaction.response.send_modal(modal)
        except Exception as e:
            logger.error(f"Error in new task: {e}")
            await interaction.response.send_message("Ein Fehler ist aufgetreten!", ephemeral=True)

    async def on_task_edit(self, interaction: nextcord.Interaction, project_id: int, task_id: int):
        """Handler für Task-Bearbeitung"""
        try:
            task = await self.service.get_task(task_id)
            if not task:
                await interaction.response.send_message("Task nicht gefunden!", ephemeral=True)
                return
            
            modal = TaskModal(project_id, task)
            await interaction.response.send_modal(modal)
        except Exception as e:
            logger.error(f"Error in task edit: {e}")
            await interaction.response.send_message("Ein Fehler ist aufgetreten!", ephemeral=True)

    async def on_task_status(self, interaction: nextcord.Interaction, project_id: int, task_id: int):
        """Handler für Task-Status Änderung"""
        try:
            task = await self.service.get_task(task_id)
            if not task:
                await interaction.response.send_message("Task nicht gefunden!", ephemeral=True)
                return
            
            # Status-Dropdown anzeigen
            options = [
                nextcord.SelectOption(label="Offen", value="open", emoji="⭕"),
                nextcord.SelectOption(label="In Arbeit", value="in_progress", emoji="🟡"),
                nextcord.SelectOption(label="Erledigt", value="done", emoji="✅")
            ]
            
            select = nextcord.ui.Select(
                placeholder="Neuen Status wählen",
                options=options,
                custom_id=f"task_status_{task_id}"
            )
            
            async def status_callback(interaction: nextcord.Interaction):
                new_status = select.values[0]
                await self.service.update_task_status(task_id, new_status)
                await self.refresh_dashboard()
                await interaction.response.send_message(f"Task-Status wurde aktualisiert!", ephemeral=True)
            
            select.callback = status_callback
            view = nextcord.ui.View(timeout=60)
            view.add_item(select)
            
            await interaction.response.send_message("Wähle den neuen Status:", view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in task status update: {e}")
            await interaction.response.send_message("Ein Fehler ist aufgetreten!", ephemeral=True)

    async def on_task_delete(self, interaction: nextcord.Interaction, project_id: int, task_id: int):
        """Handler für Task-Löschung"""
        try:
            task = await self.service.get_task(task_id)
            if not task:
                await interaction.response.send_message("Task nicht gefunden!", ephemeral=True)
                return
            
            confirm_view = ConfirmationView(title="Task löschen")
            await confirm_view.send_confirmation(
                interaction,
                f"Möchtest du den Task **{task.title}** wirklich löschen?"
            )
            
            await confirm_view.wait()
            if confirm_view.value:
                await self.service.delete_task(task_id)
                await self.refresh_dashboard()
                await interaction.followup.send("Task wurde gelöscht!", ephemeral=True)
            else:
                await interaction.followup.send("Löschung abgebrochen.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in task delete: {e}")
            await interaction.followup.send("Ein Fehler ist aufgetreten!", ephemeral=True)