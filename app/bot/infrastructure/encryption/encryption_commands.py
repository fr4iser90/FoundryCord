from nextcord.ext import commands
import nextcord
import os
import tempfile
from app.bot.infrastructure.encryption.encryption_service import EncryptionService
from app.bot.infrastructure.logging import logger
import asyncio

class EncryptionCommands(commands.Cog):
    def __init__(self, bot, encryption_service):
        self.bot = bot
        self.encryption = encryption_service

    @nextcord.slash_command(name="encrypt", description="Verschlüsselt eine Nachricht (nur per DM)")
    async def encrypt_command(self, interaction: nextcord.Interaction, message: str):
        """Verschlüsselt eine Nachricht (nur per DM)"""
        logger.info(f"Encrypt Befehl aufgerufen von {interaction.user.name}")
        
        if interaction.guild:
            await interaction.response.send_message("❌ Dieser Befehl kann nur per Direktnachricht verwendet werden.", ephemeral=True)
            return
        
        try:
            encrypted = await self.encryption.encrypt_data(message)
            await interaction.response.send_message(f"🔐 Verschlüsselte Nachricht:\n```\n{encrypted}\n```")
            logger.info(f"Nachricht erfolgreich verschlüsselt für {interaction.user.name}")
        except Exception as e:
            logger.error(f"Fehler bei der Verschlüsselung: {e}")
            await interaction.response.send_message("❌ Verschlüsselung fehlgeschlagen. Bitte versuche es später erneut.")

    @nextcord.slash_command(name="decrypt", description="Entschlüsselt eine Nachricht (nur per DM)")
    async def decrypt_command(self, interaction: nextcord.Interaction, encrypted_message: str):
        """Entschlüsselt eine Nachricht (nur per DM)"""
        logger.info(f"Decrypt Befehl aufgerufen von {interaction.user.name}")
        
        if interaction.guild:
            await interaction.response.send_message("❌ Dieser Befehl kann nur per Direktnachricht verwendet werden.", ephemeral=True)
            return
        
        try:
            decrypted = await self.encryption.decrypt_data(encrypted_message)
            await interaction.response.send_message(f"🔓 Entschlüsselte Nachricht:\n```\n{decrypted}\n```")
            logger.info(f"Nachricht erfolgreich entschlüsselt für {interaction.user.name}")
        except Exception as e:
            logger.error(f"Fehler bei der Entschlüsselung: {e}")
            await interaction.response.send_message("❌ Entschlüsselung fehlgeschlagen. Ungültige Nachricht oder Schlüssel.")

    @nextcord.slash_command(name="decrypt_file", description="Entschlüsselt eine Datei (nur per DM)")
    async def decrypt_file_command(self, interaction: nextcord.Interaction, attachment: nextcord.Attachment):
        """Entschlüsselt eine verschlüsselte Datei"""
        logger.info(f"Decrypt File Befehl aufgerufen von {interaction.user.name}")
        
        if interaction.guild:
            await interaction.response.send_message("❌ Dieser Befehl kann nur per Direktnachricht verwendet werden.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        try:
            # Temporäre Datei für den Download erstellen
            fd, temp_file_path = tempfile.mkstemp(suffix='.enc')
            os.close(fd)
            
            # Datei herunterladen
            await attachment.save(temp_file_path)
            
            # Datei entschlüsseln
            decrypted_file_path = await self.encryption.decrypt_file(temp_file_path)
            
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
                    message = await interaction.followup.send(
                        content=f"🔓 Hier ist die entschlüsselte Datei:",
                        file=discord_file,
                        ephemeral=True
                    )
                
                # Temporäre Dateien löschen
                os.remove(temp_file_path)
                os.remove(decrypted_file_path)
                
                logger.info(f"Datei erfolgreich entschlüsselt für {interaction.user.name}")

                # Nach 5 Minuten die Nachricht löschen
                try:
                    await asyncio.sleep(300)  # 5 Minuten
                    await message.delete()
                    logger.info(f"Entschlüsselte Nachricht für {interaction.user.name} wurde automatisch gelöscht")
                except Exception as e:
                    logger.error(f"Fehler beim Löschen der Nachricht: {e}")

            else:
                await interaction.followup.send("❌ Entschlüsselung fehlgeschlagen. Ungültige Datei oder Schlüssel.")
                # Temporäre Datei löschen
                os.remove(temp_file_path)
        except Exception as e:
            logger.error(f"Fehler bei der Dateientschlüsselung: {e}")
            await interaction.followup.send("❌ Entschlüsselung fehlgeschlagen. Bitte versuche es später erneut.")