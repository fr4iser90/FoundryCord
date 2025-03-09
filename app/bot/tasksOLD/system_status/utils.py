import nextcord
import asyncio
import logging

# Logger konfigurieren
logger = logging.getLogger('homelab_bot')

async def send_embed_with_retry(channel, embed, view=None, max_retries=3):
    """Sendet ein Embed mit Buttons (optional) und Wiederholungsversuchen"""
    for attempt in range(max_retries):
        try:
            await channel.purge(limit=100)
            if view:
                await channel.send(embed=embed, view=view)
            else:
                await channel.send(embed=embed)
            return True
        except nextcord.HTTPException as e:
            logger.error(f"Versuch {attempt+1}/{max_retries} fehlgeschlagen: {e}")
            await asyncio.sleep(5)
    return False