import asyncio
import nextcord
from modules.utilities.logger import logger
import datetime
import pytz


async def cleanup_homelab_channel(bot, channel_id):
    """Bereinigt den Homelab-Channel, indem Befehle und deren Antworten gelöscht werden, die älter als 3 Stunden sind."""
    try:
        channel = bot.get_channel(channel_id)
        if channel:
            logger.info(f"Starte Bereinigung des Kanals {channel_id}.")
            
            # Holen von Nachrichten aus dem Channel (letzte 200 Nachrichten)
            messages = await channel.history(limit=200).flatten()
            current_time = datetime.datetime.now(pytz.utc)  # Aktuelle Zeit in UTC (offset-aware)

            for message in messages:
                # Berechne die Differenz in Stunden zwischen der Nachricht und der aktuellen Zeit
                message_time = message.created_at.replace(tzinfo=pytz.utc)  # Sicherstellen, dass der Zeitstempel offset-aware ist
                time_difference = current_time - message_time
                hours_diff = time_difference.total_seconds() / 3600  # In Stunden umwandeln

                if hours_diff > 3:  # Wenn die Nachricht älter als 3 Stunden ist
                    bot_user_id = bot.user.id
                    if message.author.id == bot_user_id:
                        # Nur Nachrichten vom Bot löschen
                        await message.delete()
                        logger.debug(f"Gelöscht: {message.id} von {message.author} - Inhalt: {message.content}")

                    # Lösche Nachrichten, die mit "!" beginnen (Befehle) oder Antworten darauf
                    if message.content.startswith('!') or message.reference:
                        await message.delete()
                        logger.debug(f"Gelöscht: {message.id} von {message.author} - Inhalt: {message.content}")

            logger.info("Bereinigung abgeschlossen.")
        else:
            logger.error(f"Channel mit ID {channel_id} konnte nicht gefunden werden.")
    except Exception as e:
        logger.error(f"Fehler bei der Bereinigung des Kanals: {e}")


async def cleanup_task(bot, channel_id):
    """Task, der alle 30 Minuten den Homelab-Channel bereinigt."""
    await bot.wait_until_ready()

    while True:
        await cleanup_homelab_channel(bot, channel_id)
        await asyncio.sleep(1800)  # 30 Minuten warten
