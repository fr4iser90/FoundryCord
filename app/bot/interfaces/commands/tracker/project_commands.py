import nextcord
from app.bot.interfaces.commands.decorators.auth import admin_or_higher
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()
from app.shared.infrastructure.models.config import get_session
from app.shared.infrastructure.repositories import ProjectRepositoryImpl
from app.shared.infrastructure.repositories.task_repository import TaskRepository
from app.shared.domain.services.tracker.project_service import get_projects_data
from app.bot.interfaces.dashboards.controller.project_dashboard import create_task_embed
from nextcord.ext import commands

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
