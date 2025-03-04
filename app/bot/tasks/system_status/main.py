import nextcord
import asyncio
from datetime import datetime
import logging

from .collectors import collect_system_data
from .admin_status import create_admin_embed
from .public_status import create_public_embed
from .utils import send_embed_with_retry
from core.config.users import ADMINS, GUESTS

# Logger konfigurieren
logger = logging.getLogger('homelab_bot')

async def system_status_task(bot, channel_id):
    """Haupttask für System-Status-Updates"""
    logger.info(f"System-Status-Task gestartet für Kanal {channel_id}")
    
    await bot.wait_until_ready()
    logger.info("Bot ist bereit für System-Status-Updates")
    
    channel = bot.get_channel(channel_id)
    
    if not channel:
        logger.error(f"Kanal mit ID {channel_id} nicht gefunden.")
        return
    
    logger.info(f"Kanal gefunden: {channel.name}")
    
    # Debug: Berechtigungen prüfen
    logger.debug(f"Channel Permissions: {channel.permissions_for(channel.guild.me)}")
    
    # Threads erstellen oder suchen
    try:
        # Public Thread
        public_thread = next((t for t in channel.threads if t.name == "Public Status"), None)
        if not public_thread:
            public_thread = await channel.create_thread(
                name="Public Status",
                auto_archive_duration=1440,
                reason="Automatische Updates"
            )
            logger.info("Public Thread erstellt")
            
            # Gäste hinzufügen
            for guest_id in GUESTS.values():
                try:
                    guest = await channel.guild.fetch_member(int(guest_id))
                    if guest:
                        await public_thread.add_user(guest)
                        logger.info(f"Gast {guest.display_name} hinzugefügt")
                        await asyncio.sleep(1)  # Rate Limit vermeiden
                except Exception as e:
                    logger.error(f"Fehler beim Hinzufügen von Gast {guest_id}: {e}")
        
        # Admin Thread
        admin_thread = next((t for t in channel.threads if t.name == "Admin Status"), None)
        if not admin_thread:
            admin_thread = await channel.create_thread(
                name="Admin Status",
                auto_archive_duration=1440,
                reason="Automatische Updates",
                type=nextcord.ChannelType.private_thread
            )
            logger.info("Admin Thread erstellt")
            
            # Admins hinzufügen
            for admin_id in ADMINS.values():
                try:
                    admin = await channel.guild.fetch_member(int(admin_id))
                    if admin:
                        await admin_thread.add_user(admin)
                        logger.info(f"Admin {admin.display_name} hinzugefügt")
                        await asyncio.sleep(1)  # Rate Limit vermeiden
                except Exception as e:
                    logger.error(f"Fehler beim Hinzufügen von Admin {admin_id}: {e}")
        
        # Threads reaktivieren falls archiviert
        if public_thread.archived:
            await public_thread.edit(archived=False)
            logger.info("Public Thread reaktiviert")
        
        if admin_thread.archived:
            await admin_thread.edit(archived=False)
            logger.info("Admin Thread reaktiviert")
    
    except Exception as e:
        logger.error(f"Thread-Erstellung fehlgeschlagen: {e}")
        return
    
    # Hauptschleife für Status-Updates
    while True:
        try:
            # Systemdaten sammeln
            system_data = await collect_system_data()
            
            # Embeds erstellen
            public_embed = create_public_embed(system_data)
            admin_embed = create_admin_embed(system_data)
            
            # Embeds senden
            public_success = await send_embed_with_retry(public_thread, public_embed)
            admin_success = await send_embed_with_retry(admin_thread, admin_embed)
            
            if not public_success or not admin_success:
                logger.error("Kritischer Fehler beim Senden der Statusupdates")
        
        except Exception as e:
            logger.error(f"Kritischer Systemfehler: {str(e)}")
            await asyncio.sleep(60)  # Kurze Pause bei Fehlern
        
        await asyncio.sleep(300)  # 5 Minuten Wartezeit