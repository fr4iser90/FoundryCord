# @/app/bot/core/startup.py
import os
import nextcord
from modules.utilities.logger import logger 
from modules.tasks.system_status_task import system_status_task
from modules.tasks.cleanup_task import cleanup_homelab_channel  # Importiere die neue Cleanup-Task

# Liste von Startup-Aufgaben
startup_tasks = []

def add_startup_task(task_func):
    """Fügt eine Aufgabe zur Startup-Liste hinzu."""
    startup_tasks.append(task_func)

def setup_bot(bot):
    """Setzt den Eventhandler für on_ready."""
    @bot.event
    async def on_ready():
        # Kanal-ID aus den Umgebungsvariablen lesen
        discord_homelab_channel_id = int(os.getenv('DISCORD_HOMELAB_CHANNEL', '0'))  # Standardwert: 0 (falls nicht gesetzt)

        if discord_homelab_channel_id:
            channel = bot.get_channel(discord_homelab_channel_id)
            if channel:
                # Logge, dass der Bot bereit ist und welche Tasks ausgeführt werden
                logger.info(f"Bot ist bereit. Starte Aufgaben für Kanal ID: {discord_homelab_channel_id}")
                
                # Erstelle und starte alle Aufgaben in der startup_tasks-Liste
                for task in startup_tasks:
                    logger.debug(f"Starte Task: {task.__name__}")
                    bot.loop.create_task(task(bot, discord_homelab_channel_id))
            else:
                logger.error(f"Kanal mit der ID {discord_homelab_channel_id} wurde nicht gefunden.")
        else:
            logger.error("DISCORD_HOMELAB_CHANNEL ist nicht in den Umgebungsvariablen gesetzt.")


add_startup_task(system_status_task)
add_startup_task(cleanup_homelab_channel)