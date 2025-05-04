from nextcord.ext import commands
from .base_logging_service import BaseLoggingService

class BotLoggingService(commands.Cog):
    """Logging service for the Discord bot"""
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.logger = BaseLoggingService("homelab.bot")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Log incoming messages"""
        self.logger.info(f"New message from {message.author}: {message.content}", 
                 author=str(message.author), channel=str(message.channel))
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Log command errors"""
        if isinstance(error, commands.CheckFailure):
            self.logger.info(f"Permission check failed for command '{ctx.command}'", 
                     author=str(ctx.author), command=str(ctx.command))
            return
        
        self.logger.error(f"Error in command {ctx.command}", 
                  exception=error, author=str(ctx.author), command=str(ctx.command))
                  
    # Add these delegate methods to maintain the same interface
    def info(self, message, **context):
        return self.logger.info(message, **context)
        
    def error(self, message, exception=None, **context):
        return self.logger.error(message, exception=exception, **context)
        
    def debug(self, message, **context):
        return self.logger.debug(message, **context)
        
    def warning(self, message, **context):
        return self.logger.warning(message, **context)

    def critical(self, message, exception=None, **context):
        return self.logger.critical(message, exception=exception, **context)