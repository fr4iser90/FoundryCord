import nextcord
from app.bot.utils.decorators.auth import admin_or_higher
from app.shared.logging import logger
from app.shared.infrastructure.database.models.config import get_session
from app.shared.infrastructure.database.repositories.project_repository_impl import ProjectRepository
from app.shared.infrastructure.database.repositories.task_repository import TaskRepository
from app.bot.domain.tracker.services.project_service import get_projects_data
from app.bot.interfaces.dashboards.controller.project_dashboard import create_task_embed

async def check_tracker_thread(interaction):
    """Überprüft, ob der Befehl im Projekt-Tracker-Thread ausgeführt wird"""
    channel = interaction.channel
    
    if not isinstance(channel, nextcord.Thread) or channel.name != "Projekt Tracker":
        await interaction.response.send_message(
            "⚠️ Dieser Befehl kann nur im 'Projekt Tracker'-Thread verwendet werden!", 
            ephemeral=True
        )
        logger.info(f"Benutzer {interaction.user.name} versuchte, einen Projekt-Tracker-Befehl außerhalb des Threads zu verwenden.")
        return False
    return True

async def setup(bot):
    """Setup function for the project tracker commands"""
    try:
        # Slash-Commands für Projekte
        @bot.slash_command(name="project_add", description="Fügt ein neues Projekt hinzu")
        @admin_or_higher()
        async def add_project(interaction: nextcord.Interaction, name: str):
            # Thread-Check
            if not await check_tracker_thread(interaction):
                return
            
            # ... existing code ...
        
        # Weitere Slash-Commands hier...
        
        # Hinzufügen aller anderen project_* und task_* Befehle
        # ...

        logger.info("Project tracker commands initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize project tracker commands: {e}")
        raise
