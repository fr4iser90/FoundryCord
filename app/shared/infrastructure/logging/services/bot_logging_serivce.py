from nextcord.ext import commands
from .base_logging_service import BaseLoggingService

class BotLoggingService(BaseLoggingService, commands.Cog):
    """Logging service for the Discord bot"""
    
    def __init__(self, bot):
        BaseLoggingService.__init__(self, "homelab.bot")
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Log incoming messages"""
        self.info(f"New message from {message.author}: {message.content}", 
                 author=str(message.author), channel=str(message.channel))
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Log command errors"""
        if isinstance(error, commands.CheckFailure):
            self.info(f"Permission check failed for command '{ctx.command}'", 
                     author=str(ctx.author), command=str(ctx.command))
            return
        
        self.error(f"Error in command {ctx.command}", 
                  exception=error, author=str(ctx.author), command=str(ctx.command))