import os
import nextcord
from nextcord.ext import commands
from core.utilities.logger import logger
from core.decorators.auth import super_admin_or_higher, user_or_higher
from modules.wireguard.utils.get_user_config import get_user_config
from core.middleware.encryption_middleware import EncryptionMiddleware

class WireguardQRCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "/app/bot/database/wireguard"
        self.encryption = EncryptionMiddleware(bot)

    @nextcord.slash_command(name="wireguard_qr", description="Holt deinen eigenen Wireguard QR-Code")
    @user_or_higher()
    async def wireguard_qr(self, interaction: nextcord.Interaction):
        """Sendet dem Benutzer automatisch seinen WireGuard-QR-Code basierend auf dem Discord-Namen."""
        await interaction.response.defer(ephemeral=True)
        
        username = interaction.user.name  # Holt den Discord-Namen
        logger.debug(f"Executing wireguard_qr command for user: {username}")
        
        user_config = get_user_config(self.config_path, username)
        
        if user_config:
            user_dir = os.path.join(self.config_path, f"peer_{username}")
            qr_code_file = os.path.join(user_dir, f"peer_{username}.png")
            
            if os.path.exists(qr_code_file):
                logger.debug(f"Using existing QR code file: {qr_code_file}")
                # Datei senden
                try:
                    # Verschlüssele die Datei
                    encrypted_file_path = await self.encryption.encrypt_file(qr_code_file)
                    
                    if encrypted_file_path:
                        with open(encrypted_file_path, 'rb') as file:
                            # Erstelle ein File-Objekt für Discord
                            discord_file = nextcord.File(file, filename=f"wireguard_config_{username}.enc")
                            # Sende die Datei als DM
                            try:
                                await interaction.user.send(
                                    content="🔒 Hier ist dein verschlüsselter Wireguard QR-Code. Verwende `/decrypt_file` um ihn zu entschlüsseln:",
                                    file=discord_file
                                )
                                await interaction.followup.send("✅ Verschlüsselter QR-Code wurde dir als private Nachricht gesendet!", ephemeral=True)
                            except nextcord.Forbidden:
                                await interaction.followup.send("❌ Ich konnte dir keine DM senden. Bitte aktiviere DMs von Servermitgliedern.", ephemeral=True)
                        
                        # Temporäre verschlüsselte Datei löschen
                        os.remove(encrypted_file_path)
                    else:
                        await interaction.followup.send("❌ Fehler bei der Verschlüsselung des QR-Codes.", ephemeral=True)
                except Exception as e:
                    logger.error(f"Error sending QR code file: {e}")
                    await interaction.followup.send("❌ Fehler beim Senden des QR-Codes.", ephemeral=True)
            else:
                logger.warning(f"QR code file not found for user {username} at path: {qr_code_file}")
                await interaction.followup.send("❌ QR-Code für deinen Benutzer nicht gefunden.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Keine Wireguard-Konfiguration für deinen Benutzer gefunden.", ephemeral=True)

    @nextcord.slash_command(name="wireguard_get_user_qr", description="Holt den Wireguard QR-Code eines bestimmten Benutzers")
    @super_admin_or_higher()
    async def wireguard_get_user_qr(self, interaction: nextcord.Interaction, username: str):
        """Sendet die WireGuard-Config eines bestimmten Users als QR-Code."""
        await interaction.response.defer(ephemeral=True)
        
        logger.debug(f"Executing get_user_qr command for user: {username}")
        
        user_config = get_user_config(self.config_path, username)
        
        if user_config:
            user_dir = os.path.join(self.config_path, f"peer_{username}")
            qr_code_file = os.path.join(user_dir, f"peer_{username}.png")
            
            if os.path.exists(qr_code_file):
                logger.debug(f"Using existing QR code file: {qr_code_file}")
                # Datei senden
                try:
                    # Verschlüssele die Datei
                    encrypted_file_path = await self.encryption.encrypt_file(qr_code_file)
                    
                    if encrypted_file_path:
                        with open(encrypted_file_path, 'rb') as file:
                            # Erstelle ein File-Objekt für Discord
                            discord_file = nextcord.File(file, filename=f"wireguard_config_{username}.enc")
                            # Sende die Datei als DM
                            try:
                                await interaction.user.send(
                                    content=f"🔒 Hier ist der verschlüsselte Wireguard QR-Code für Benutzer {username}. Verwende `/decrypt_file` um ihn zu entschlüsseln:",
                                    file=discord_file
                                )
                                await interaction.followup.send(f"✅ Verschlüsselter QR-Code für {username} wurde dir als private Nachricht gesendet!", ephemeral=True)
                            except nextcord.Forbidden:
                                await interaction.followup.send("❌ Ich konnte dir keine DM senden. Bitte aktiviere DMs von Servermitgliedern.", ephemeral=True)
                        
                        # Temporäre verschlüsselte Datei löschen
                        os.remove(encrypted_file_path)
                    else:
                        await interaction.followup.send("❌ Fehler bei der Verschlüsselung des QR-Codes.", ephemeral=True)
                except Exception as e:
                    logger.error(f"Error sending QR code file: {e}")
                    await interaction.followup.send("❌ Fehler beim Senden des QR-Codes.", ephemeral=True)
            else:
                logger.warning(f"QR code file not found for user {username} at path: {qr_code_file}")
                await interaction.followup.send(f"❌ QR-Code für Benutzer {username} nicht gefunden.", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Keine Wireguard-Konfiguration für Benutzer {username} gefunden.", ephemeral=True)

def setup(bot):
    bot.add_cog(WireguardQRCommands(bot))