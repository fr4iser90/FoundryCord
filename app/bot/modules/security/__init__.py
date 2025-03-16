from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from .cogs.security_cog import SecurityCommands

async def setup(bot):
    """Setup function for the security module"""
    try:
        cog = SecurityCommands(bot)
        bot.add_cog(cog)
        logger.info("Security commands initialized successfully")
        return cog
    except Exception as e:
        logger.error(f"Failed to initialize security: {e}")
        raise