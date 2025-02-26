import asyncio
import logging
import discord
from nextcord.ext import commands

class RateLimitMiddleware(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        """Fehler-Handler für Rate-Limiting."""
        if isinstance(event, discord.errors.RateLimited):
            retry_after = event.retry_after  # Zeit bis zur nächsten Anfrage
            logging.warning(f"Rate-Limited! Retry after {retry_after:.2f} seconds.")
            await asyncio.sleep(retry_after)  # Warten bis das Rate-Limit zurückgesetzt wird
        else:
            logging.error(f"Unbehandelte Fehlermeldung: {event}")

    async def delete_message(self, message):
        """Löscht eine Nachricht und behandelt Rate-Limits."""
        try:
            await message.delete()
            await asyncio.sleep(0.75)
        except discord.errors.RateLimited as e:
            retry_after = e.retry_after
            logging.warning(f"Rate-Limited während Löschung! Retry after {retry_after:.2f} seconds.")
            await asyncio.sleep(retry_after)  # Warten, bis das Rate-Limit zurückgesetzt wird
            await message.delete()  # Löscht nach der Verzögerung

def setup(bot):
    bot.add_cog(RateLimitMiddleware(bot))  # Füge die RateLimitMiddleware hinzu
