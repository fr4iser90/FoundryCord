"""
Shared logging package that supports both bot and web applications
through dependency injection.
"""
# Import only the logger which is common to both bot and web components
from .logger import bot_logger, web_logger, db_logger, logger

# Import service factories rather than direct classes
def get_bot_logging_service():
    """Factory function to get bot logging service only when needed"""
    from .logging_service import LoggingService
    return LoggingService

def get_web_logging_service():
    """Factory function to get web logging service only when needed"""
    from .web_logging_service import WebLoggingService
    return WebLoggingService

async def setup(bot):
    """Initialize the Logging service for the bot"""
    try:
        LoggingService = get_bot_logging_service()
        logging_service = LoggingService(bot)
        bot.add_cog(logging_service)
        bot_logger.info("Bot logging service initialized successfully")
        return logging_service
    except Exception as e:
        bot_logger.error(f"Failed to initialize bot logging service: {e}")
        raise

def setup_web(app):
    """Initialize the Web Logging service"""
    try:
        WebLoggingService = get_web_logging_service()
        web_logging_service = WebLoggingService(app)
        web_logging_service.setup_request_logging()
        web_logger.info("Web logging service initialized successfully")
        return web_logging_service
    except Exception as e:
        web_logger.error(f"Failed to initialize web logging service: {e}")
        raise