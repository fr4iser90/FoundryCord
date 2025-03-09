from .logging_service import LoggingService
from .logger import logger

async def setup(bot):
    """Initialize the Logging service"""
    try:
        logging_service = LoggingService(bot)
        bot.add_cog(logging_service)
        logger.info("Logging service initialized successfully")
        return logging_service
    except Exception as e:
        logger.error(f"Failed to initialize logging service: {e}")
        raise