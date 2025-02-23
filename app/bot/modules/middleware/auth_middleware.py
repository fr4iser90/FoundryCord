# bot/modules/middleware/auth_middleware.py
from nextcord.ext import commands
from modules.auth.permissions import is_authorized  # Importiere die Berechtigungsprüfung

def setup(bot):
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        ctx = await bot.get_context(message)

        if not is_authorized(ctx.author):
            await ctx.send("You are not authorized to use this bot.")
            return

        await bot.process_commands(message)
