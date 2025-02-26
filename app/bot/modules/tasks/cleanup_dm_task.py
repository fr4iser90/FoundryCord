# modules/tasks/cleanup_dm_task.py
import asyncio
import nextcord
from core.utilities.logger import logger
import datetime
import pytz


async def cleanup_dm_messages(bot):
    """Bereinigt DM-Nachrichten, indem Nachrichten gelöscht werden, die älter als 3 Stunden sind."""
    try:
        logger.info("Starte Bereinigung der DM-Nachrichten.")
        
        # Holen der letzten 200 DM-Nachrichten aus den Channels des Bots
        messages = []
        logger.debug(f"Verfügbare DM-Channels: {len(bot.private_channels)}")
        
        for channel in bot.private_channels:
            if isinstance(channel, nextcord.DMChannel):
                logger.debug(f"Verarbeite DM-Channel: {channel.id} mit {channel.recipient}")
                if channel.me:  # Nur Channels, in denen der Bot aktiv ist
                    channel_messages = await channel.history(limit=200).flatten()
                    logger.debug(f"Gefundene Nachrichten in {channel.id}: {len(channel_messages)}")
                    messages.extend(channel_messages)
        
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

        logger.info("Bereinigung der DMs abgeschlossen.")
    except Exception as e:
        logger.error(f"Fehler bei der Bereinigung der DMs: {e}")


async def cleanup_dm_task(bot, channel_id=None):
    """Task, der alle 30 Minuten die DM-Nachrichten bereinigt."""
    logger.debug("Initializing cleanup_dm_task")
    await bot.wait_until_ready()
    logger.debug("Bot is ready, starting cleanup loop")

    while True:
        logger.debug("Starting cleanup cycle")
        await cleanup_dm_messages(bot)
        logger.debug("Cleanup cycle completed, sleeping for 30 minutes")
        await asyncio.sleep(1800)  # 30 Minuten warten
