# app/shared/logging/logging_service.py
from nextcord.ext import commands
from .logger import bot_logger

class LoggingService(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Log the incoming message
        bot_logger.info(f"New message from {message.author}: {message.content}")
        return  # Suppress the exception
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Error handling for permission checks
        if isinstance(error, commands.CheckFailure):
            bot_logger.info(f"Permission check failed for command '{ctx.command}': {ctx.author} is not authorized.")
            return  # Suppress the exception

        # Error handling for other errors
        bot_logger.error(f"Error in command {ctx.command}: {error}")