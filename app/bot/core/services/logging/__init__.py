from .logging_service import LoggingService
from .logging_commands import logger

async def setup(bot):
    """Initialize the Logging service"""
    try:
        bot.add_cog(LoggingService(bot))
        logger.info("Logging service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize logging service: {e}")
        raise