import asyncio
import nextcord
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()
import datetime
import pytz

async def log_all_dm_channels(bot):
    """Protokolliert alle privaten DM-Kanäle des Bots."""
    try:
        logger.info("Starte DM-Kanal-Überprüfung für alle Benutzer.")
        dms = []
        
        # Durchlaufe alle Benutzer, mit denen der Bot interagiert hat
        for user in bot.users:
            try:
                if user.bot:
                    continue  # Ignoriere andere Bots
                
                if user.dm_channel is None:
                    await user.create_dm()
                if user.dm_channel:
                    dms.append((user.id, user.name, user.dm_channel.id))
                    logger.info(f"Gefundener DM-Kanal: {user.name} ({user.id}) - Kanal-ID: {user.dm_channel.id}")
            except nextcord.NotFound:
                logger.warning(f"Benutzer {user.id} nicht gefunden.")
            except nextcord.Forbidden:
                logger.warning(f"Kein Zugriff auf DM von Benutzer {user.id}.")
            except Exception as e:
                logger.error(f"Fehler beim Abrufen von DM-Kanal für {user.id}: {e}")
        
        return dms
    except Exception as e:
        logger.error(f"Fehler beim Protokollieren der DM-Kanäle: {e}")
        return []

async def cleanup_dm_messages(bot):
    """Bereinigt DM-Nachrichten, indem Nachrichten gelöscht werden, die älter als 3 Stunden sind."""
    try:
        logger.info("Starte Bereinigung der DM-Nachrichten.")
        
        dm_channels = await log_all_dm_channels(bot)
        current_time = datetime.datetime.now(pytz.utc)
        
        for user_id, user_name, channel_id in dm_channels:
            try:
                channel = bot.get_channel(channel_id)
                if not channel:
                    logger.warning(f"DM-Kanal {channel_id} für {user_name} nicht gefunden, überspringe...")
                    continue
            except Exception as e:
                logger.error(f"Fehler beim Zugriff auf Kanal {channel_id}: {e}")
                continue
                
            try:
                async for message in channel.history(limit=None):
                    if message.author.id != bot.user.id:
                        continue  # Nur eigene Nachrichten löschen
                    message_time = message.created_at.replace(tzinfo=pytz.utc)
                    time_difference = current_time - message_time
                    
                    if time_difference.total_seconds() > 10800:  # 3 Stunden in Sekunden
                        try:
                            await message.delete()
                            logger.debug(f"Gelöscht: {message.id} von {message.author} - Inhalt: {message.content}")
                            await asyncio.sleep(0.75)  # Rate-Limit-Schutz
                        except nextcord.NotFound:
                            logger.warning(f"Nachricht {message.id} nicht gefunden, vermutlich bereits gelöscht.")
                            continue
                        except nextcord.Forbidden as e:
                            logger.error(f"Löschen verboten: {e}")
                            break
                        except Exception as e:
                            logger.error(f"Fehler beim Löschen der Nachricht {message.id}: {e}")
                            await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Fehler beim Durchsuchen des Kanalverlaufs: {e}")
        
        logger.info("Bereinigung der DMs abgeschlossen.")
    except Exception as e:
        logger.error(f"Fehler bei der Bereinigung der DMs: {e}")

async def cleanup_dm_task(bot, channel_id=None):
    """Task, der alle 30 Minuten die DM-Nachrichten bereinigt.
    
    Args:
        bot: The bot instance
        channel_id: Optional channel ID for logging purposes
    """
    logger.debug("Initialisiere cleanup_dm_task")
    await bot.wait_until_ready()
    logger.debug("Bot ist bereit, starte Bereinigungsschleife")
    
    while True:
        await cleanup_dm_messages(bot)
        logger.debug("Bereinigungszyklus abgeschlossen, warte 30 Minuten")
        await asyncio.sleep(1800)