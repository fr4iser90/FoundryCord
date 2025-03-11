from .rate_limiting_service import RateLimitingService
from .rate_limiting_middleware import RateLimitingMiddleware
from infrastructure.logging import logger

__all__ = ['RateLimitingService', 'RateLimitingMiddleware', 'setup']

async def setup(bot):
    """Central initialization of the Rate Limiting service"""
    try:
        # Initialize rate limiting service
        rate_limiting_service = RateLimitingService(bot)
        bot.rate_limiting = rate_limiting_service
        
        # Initialize middleware with service instance
        middleware = RateLimitingMiddleware(bot, rate_limiting_service)
        bot.add_cog(middleware)
        
        logger.info("Rate limiting service and middleware initialized successfully")
        logger.info("Rate limiting now protects all interactions including dashboards, buttons and components")
        
        return rate_limiting_service
    except Exception as e:
        logger.error(f"Failed to initialize rate limiting service: {e}")
        raise
