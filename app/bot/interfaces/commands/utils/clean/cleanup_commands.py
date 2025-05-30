import nextcord
from nextcord.ext import commands
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.interfaces.commands.decorators.auth import admin_or_higher
from app.bot.application.tasks.cleanup_task import cleanup_homelab_channel
from app.bot.application.tasks.cleanup_dm_task import cleanup_dm_messages
import traceback

def setup(bot):
    @bot.slash_command(name="cleanup_channel", description="Bereinigt den Homelab-Channel manuell")
    @admin_or_higher()
    async def cleanup_channel_command(interaction: nextcord.Interaction):
        """Manuelles Auslösen der Kanalbereinigung"""
        try:
            await interaction.response.defer(ephemeral=True)
            logger.info("Manuelle Kanalbereinigung über Command ausgelöst")
            
            # Hole die Channel-ID aus der Umgebung oder verwende die aktuelle
            channel_id = interaction.channel_id
            
            # Verwende interaction.client statt bot
            await cleanup_homelab_channel(interaction.client, channel_id)
            await interaction.followup.send("Kanalbereinigung abgeschlossen", ephemeral=True)
        except Exception as e:
            error_msg = f"Fehler bei der Kanalbereinigung: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            try:
                await interaction.followup.send(error_msg, ephemeral=True)
            except:
                pass
    
    @bot.slash_command(name="cleanup_dms", description="Löst die Bereinigung der DMs manuell aus")
    @admin_or_higher()
    async def cleanup_dms_command(interaction: nextcord.Interaction):
        """Manuelles Auslösen der DM-Bereinigung"""
        try:
            await interaction.response.defer(ephemeral=True)
            logger.info("Manuelle DM-Bereinigung über Command ausgelöst")
            # Verwende interaction.client statt bot
            await cleanup_dm_messages(interaction.client)
            await interaction.followup.send("DM-Bereinigung abgeschlossen", ephemeral=True)
        except Exception as e:
            error_msg = f"Fehler bei der DM-Bereinigung: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            try:
                await interaction.followup.send(error_msg, ephemeral=True)
            except:
                pass