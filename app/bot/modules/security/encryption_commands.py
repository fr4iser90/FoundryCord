from nextcord.ext import commands
import nextcord
import os
import tempfile
from core.middleware.encryption_middleware import EncryptionMiddleware
from core.utilities.logger import logger

class EncryptionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.encryption = EncryptionMiddleware(bot)

def setup(bot):
    # Einzelne Slash-Commands für Verschlüsselung
    @bot.slash_command(name="encrypt", description="Verschlüsselt eine Nachricht (nur per DM)")
    async def encrypt_command(interaction: nextcord.Interaction, message: str):
        """Verschlüsselt eine Nachricht (nur per DM)"""
        logger.info(f"Encrypt Befehl aufgerufen von {interaction.user.name}")
        
        # Prüfen, ob der Befehl in einem Server oder per DM ausgeführt wird
        if interaction.guild:
            await interaction.response.send_message("❌ Dieser Befehl kann nur per Direktnachricht verwendet werden.", ephemeral=True)
            return
        
        # Encryption Middleware initialisieren
        encryption = EncryptionMiddleware(bot)
        
        try:
            encrypted = await encryption.encrypt_data(message)
            await interaction.response.send_message(f"🔐 Verschlüsselte Nachricht:\n```\n{encrypted}\n```")
            logger.info(f"Nachricht erfolgreich verschlüsselt für {interaction.user.name}")
        except Exception as e:
            logger.error(f"Fehler bei der Verschlüsselung: {e}")
            await interaction.response.send_message("❌ Verschlüsselung fehlgeschlagen. Bitte versuche es später erneut.")

    @bot.slash_command(name="decrypt", description="Entschlüsselt eine Nachricht (nur per DM)")
    async def decrypt_command(interaction: nextcord.Interaction, encrypted_message: str):
        """Entschlüsselt eine Nachricht (nur per DM)"""
        logger.info(f"Decrypt Befehl aufgerufen von {interaction.user.name}")
        
        # Prüfen, ob der Befehl in einem Server oder per DM ausgeführt wird
        if interaction.guild:
            await interaction.response.send_message("❌ Dieser Befehl kann nur per Direktnachricht verwendet werden.", ephemeral=True)
            return
        
        # Encryption Middleware initialisieren
        encryption = EncryptionMiddleware(bot)
        
        try:
            decrypted = await encryption.decrypt_data(encrypted_message)
            await interaction.response.send_message(f"🔓 Entschlüsselte Nachricht:\n```\n{decrypted}\n```")
            logger.info(f"Nachricht erfolgreich entschlüsselt für {interaction.user.name}")
        except Exception as e:
            logger.error(f"Fehler bei der Entschlüsselung: {e}")
            await interaction.response.send_message("❌ Entschlüsselung fehlgeschlagen. Ungültige Nachricht oder Schlüssel.")

    @bot.slash_command(name="decrypt_file", description="Entschlüsselt eine Datei (nur per DM)")
    async def decrypt_file_command(interaction: nextcord.Interaction, attachment: nextcord.Attachment):
        """Entschlüsselt eine verschlüsselte Datei"""
        logger.info(f"Decrypt File Befehl aufgerufen von {interaction.user.name}")
        
        # Prüfen, ob der Befehl in einem Server oder per DM ausgeführt wird
        if interaction.guild:
            await interaction.response.send_message("❌ Dieser Befehl kann nur per Direktnachricht verwendet werden.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        # Encryption Middleware initialisieren
        encryption = EncryptionMiddleware(bot)
        
        try:
            # Temporäre Datei für den Download erstellen
            fd, temp_file_path = tempfile.mkstemp(suffix='.enc')
            os.close(fd)
            
            # Datei herunterladen
            await attachment.save(temp_file_path)
            
            # Datei entschlüsseln
            decrypted_file_path = await encryption.decrypt_file(temp_file_path)
            
            if decrypted_file_path:
                # Originaldateiname extrahieren (ohne .enc)
                original_filename = os.path.splitext(attachment.filename)[0]
                if original_filename.endswith('.enc'):
                    original_filename = os.path.splitext(original_filename)[0]
                
                # Dateiendung aus dem entschlüsselten Inhalt bestimmen
                # Hier vereinfacht, könnte erweitert werden
                if original_filename.endswith('.png'):
                    mime_type = 'image/png'
                elif original_filename.endswith('.conf'):
                    mime_type = 'text/plain'
                else:
                    mime_type = 'application/octet-stream'
                    original_filename += '.bin'
                
                # Entschlüsselte Datei senden
                with open(decrypted_file_path, 'rb') as file:
                    discord_file = nextcord.File(file, filename=original_filename)
                    await interaction.followup.send(
                        content=f"🔓 Hier ist die entschlüsselte Datei:",
                        file=discord_file
                    )
                
                # Temporäre Dateien löschen
                os.remove(temp_file_path)
                os.remove(decrypted_file_path)
                
                logger.info(f"Datei erfolgreich entschlüsselt für {interaction.user.name}")
            else:
                await interaction.followup.send("❌ Entschlüsselung fehlgeschlagen. Ungültige Datei oder Schlüssel.")
                # Temporäre Datei löschen
                os.remove(temp_file_path)
        except Exception as e:
            logger.error(f"Fehler bei der Dateientschlüsselung: {e}")
            await interaction.followup.send("❌ Entschlüsselung fehlgeschlagen. Bitte versuche es später erneut.")