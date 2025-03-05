# tasks/project_tracker_task.py
import asyncio
import nextcord
from datetime import datetime
from core.services.auth.models.users import SUPER_ADMINS, ADMINS
from core.services.logging.logging_commands import logger
from modules.tracker.project_tracker import create_task_embed, load_tasks

async def project_tracker_task(bot, channel_id):
    """Task für den Projekt-Tracker"""
    await bot.wait_until_ready()
    logger.info("Initialisiere Projekt-Tracker Task")
    
    channel = bot.get_channel(channel_id)
    if not channel:
        logger.error(f"Kanal mit ID {channel_id} nicht gefunden.")
        return
    
    # Admin-Thread erstellen oder suchen
    try:
        tracker_thread = next((t for t in channel.threads if t.name == "Projekt Tracker"), None)
        if not tracker_thread:
            tracker_thread = await channel.create_thread(
                name="Projekt Tracker",
                auto_archive_duration=1440,
                reason="Projekt-Tracking",
                type=nextcord.ChannelType.private_thread
            )
            logger.info("Projekt Tracker Thread erstellt")
        
        # Super-Admins und Admins hinzufügen (jetzt außerhalb der if-Bedingung)
        all_admins = {**SUPER_ADMINS, **ADMINS}  # Kombiniere beide Dictionaries
        for admin_id in all_admins.values():
            try:
                admin = await channel.guild.fetch_member(int(admin_id))
                if admin:
                    await tracker_thread.add_user(admin)
                    logger.info(f"Admin {admin.display_name} zum Tracker hinzugefügt")
                    await asyncio.sleep(1)  # Rate Limit vermeiden
            except Exception as e:
                logger.error(f"Fehler beim Hinzufügen von Admin {admin_id}: {e}")
        
        # Thread reaktivieren falls archiviert
        if tracker_thread.archived:
            await tracker_thread.edit(archived=False)
            logger.info("Projekt Tracker Thread reaktiviert")
            
    except Exception as e:
        logger.error(f"Thread-Erstellung fehlgeschlagen: {e}")
        return
    
    # Initiale Nachricht senden
    try:
        await tracker_thread.purge(limit=100)
        tasks_data = load_tasks()
        embed = create_task_embed(tasks_data)
        await tracker_thread.send(embed=embed)
        
        # Willkommensnachricht mit Befehlen
        help_embed = nextcord.Embed(
            title="🔍 Projekt Tracker Hilfe",
            description="Hier sind die verfügbaren Befehle:",
            color=0x2ecc71
        )
        help_embed.add_field(
            name="Projekte",
            value=(
                "`/project_add [name]` - Neues Projekt erstellen\n"
                "`/project_delete [name]` - Projekt löschen\n"
                "`/project_list` - Alle Projekte anzeigen"
            ),
            inline=False
        )
        help_embed.add_field(
            name="Aufgaben",
            value=(
                "`/task_add [projekt] [titel] [beschreibung] [priorität]` - Neue Aufgabe\n"
                "`/task_complete [projekt] [aufgaben-id]` - Aufgabe als erledigt markieren\n"
                "`/task_delete [projekt] [aufgaben-id]` - Aufgabe löschen"
            ),
            inline=False
        )
        await tracker_thread.send(embed=help_embed)
        
    except Exception as e:
        logger.error(f"Fehler beim Initialisieren des Trackers: {e}")
    
    # Regelmäßiges Update
    while True:
        try:
            await asyncio.sleep(3600)  # Stündliches Update
            tasks_data = load_tasks()
            embed = create_task_embed(tasks_data)
            await tracker_thread.purge(limit=100)
            await tracker_thread.send(embed=embed)
            logger.info("Projekt Tracker automatisch aktualisiert")
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Trackers: {e}")
            await asyncio.sleep(300)  # 5 Minuten Pause bei Fehlern