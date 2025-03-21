import os
import nextcord
from nextcord.ext import commands
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.utils.decorators.auth import bot_owner_only, user_or_higher
from app.bot.interfaces.commands.wireguard.utils import get_user_config
import asyncio

class WireguardConfigCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "/app/bot/database/wireguard"

    @nextcord.slash_command(name="wireguard_config", description="Holt deine Wireguard-Konfigurationsdatei")
    @user_or_higher()
    async def wireguard_config(self, interaction: nextcord.Interaction):
        """Sendet dem Benutzer automatisch das wireguard conf file basierend auf dem Discord-Namen."""
        await interaction.response.defer(ephemeral=True)
        
        username = interaction.user.name
        logger.info(f"User attempting to get config: {username}")
        
        user_dir = os.path.join(self.config_path, f"peer_{username}")
        config_file = os.path.join(user_dir, f"peer_{username}.conf")
        logger.info(f"Looking for config file at: {config_file}")
        logger.info(f"Config file exists: {os.path.exists(config_file)}")
        
        user_config = get_user_config(self.config_path, username)
        
        if user_config:
            user_dir = os.path.join(self.config_path, f"peer_{username}")
            config_file = os.path.join(user_dir, f"peer_{username}.conf")
            
            if os.path.exists(config_file):
                logger.debug(f"Using existing config file: {config_file}")
                try:
                    # Verschlüssele die Datei
                    encrypted_file_path = await self.bot.encryption.encrypt_file(config_file)
                    
                    if encrypted_file_path:
                        with open(encrypted_file_path, 'rb') as file:
                            discord_file = nextcord.File(file, filename=f"wireguard_config_{username}.enc")
                            await interaction.user.send(
                                content="🔒 Hier ist deine verschlüsselte Wireguard-Konfigurationsdatei:",
                                file=discord_file
                            )
                            await interaction.followup.send("✅ Verschlüsselte Konfigurationsdatei wurde dir als private Nachricht gesendet!", ephemeral=True)
                        
                        # Temporäre verschlüsselte Datei löschen
                        os.remove(encrypted_file_path)
                    else:
                        await interaction.followup.send("❌ Fehler bei der Verschlüsselung der Konfigurationsdatei.", ephemeral=True)
                except Exception as e:
                    logger.error(f"Error sending config file: {e}")
                    await interaction.followup.send("❌ Fehler beim Senden der Konfigurationsdatei.", ephemeral=True)
            else:
                logger.warning(f"Config file not found for user {username} at path: {config_file}")
                await interaction.followup.send("❌ Konfigurationsdatei für deinen Benutzer nicht gefunden.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Keine Wireguard-Konfiguration für deinen Benutzer gefunden.", ephemeral=True)

    @nextcord.slash_command(name="wireguard_get_config_from_user", description="Holt die Konfigurationsdatei eines bestimmten Benutzers")
    @bot_owner_only()
    async def wireguard_get_config_from_user(self, interaction: nextcord.Interaction, username: str):
        """Gibt die Konfigurationsdatei eines bestimmten WireGuard-Users zurück."""
        await interaction.response.defer(ephemeral=True)
        
        logger.debug(f"Executing get_user_config slash command for user: {username}")
        
        user_config = get_user_config(self.config_path, username)
        
        if user_config:
            user_dir = os.path.join(self.config_path, f"peer_{username}")
            config_file = os.path.join(user_dir, f"peer_{username}.conf")
            
            if os.path.exists(config_file):
                logger.debug(f"Using existing config file: {config_file}")
                try:
                    # Verschlüssele die Datei
                    encrypted_file_path = await self.bot.encryption.encrypt_file(config_file)
                    
                    if encrypted_file_path:
                        with open(encrypted_file_path, 'rb') as file:
                            discord_file = nextcord.File(file, filename=f"wireguard_config_{username}.enc")
                            await interaction.user.send(
                                content=f"🔒 Hier ist die verschlüsselte Wireguard-Konfigurationsdatei für Benutzer {username}:",
                                file=discord_file
                            )
                            await interaction.followup.send(f"✅ Verschlüsselte Konfigurationsdatei für {username} wurde dir als private Nachricht gesendet!", ephemeral=True)
                        
                        # Temporäre verschlüsselte Datei löschen
                        os.remove(encrypted_file_path)
                    else:
                        await interaction.followup.send("❌ Fehler bei der Verschlüsselung der Konfigurationsdatei.", ephemeral=True)
                except Exception as e:
                    logger.error(f"Error sending config file: {e}")
                    await interaction.followup.send("❌ Fehler beim Senden der Konfigurationsdatei.", ephemeral=True)
            else:
                logger.warning(f"Config file not found for user {username} at path: {config_file}")
                await interaction.followup.send(f"❌ Konfigurationsdatei für Benutzer {username} nicht gefunden.", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Keine Wireguard-Konfiguration für Benutzer {username} gefunden.", ephemeral=True)

async def setup(bot):
    # Warte bis encryption service verfügbar ist
    while not hasattr(bot, 'encryption'):
        await asyncio.sleep(1)
    await bot.add_cog(WireguardConfigCommands(bot))