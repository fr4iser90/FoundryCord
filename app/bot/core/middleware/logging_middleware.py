# modules/core/logging_middleware.py
from nextcord.ext import commands
from core.services.logging.logging_commands import logger

class LoggingMiddleware(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Logge die eingehende Nachricht
        logger.info(f"Neue Nachricht von {message.author}: {message.content}")
        return # Unterdrücke die Exception
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Fehlerbehandlung für Berechtigungsprüfungen
        if isinstance(error, commands.CheckFailure):
            logger.info(f"Berechtigungsprüfung fehlgeschlagen für Befehl '{ctx.command}': {ctx.author} ist nicht berechtigt.")
            return  # Unterdrücke die Exception

        # Fehlerbehandlung für andere Fehler
        logger.error(f"Fehler im Befehl {ctx.command}: {error}")

def setup(bot):
    bot.add_cog(LoggingMiddleware(bot))  # Füge die LoggingMiddleware hinzu
