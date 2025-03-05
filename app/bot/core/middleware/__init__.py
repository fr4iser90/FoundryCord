from core.services.logging.logging_commands import logger

#from .logging_middleware import LoggingMiddleware
from .rate_limit_middleware import RateLimitMiddleware

async def setup(bot):
    """Zentrale Initialisierung der Middleware"""
    try:
        
        # Andere Middleware initialisieren...
        bot.add_cog(RateLimitMiddleware(bot))
        #bot.add_cog(LoggingMiddleware(bot))

        
        logger.info("Middleware initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize middleware: {e}")
        raise
