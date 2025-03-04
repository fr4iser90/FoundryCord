from nextcord.ext import commands

class LoggingEvents(commands.Cog):
    def __init__(self, bot, logging_service):
        self.bot = bot
        self.logger = logging_service

    @commands.Cog.listener()
    async def on_message(self, message):
        self.logger.info(f"Neue Nachricht von {message.author}: {message.content}")
        return

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            self.logger.info(
                f"Berechtigungsprüfung fehlgeschlagen für Befehl '{ctx.command}': "
                f"{ctx.author} ist nicht berechtigt."
            )
            return

        self.logger.error(f"Fehler im Befehl {ctx.command}: {error}")