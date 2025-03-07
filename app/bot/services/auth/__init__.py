# app/bot/services/auth/__init__.py
from .authentication_service import AuthenticationService
from .authorization_service import AuthorizationService
from infrastructure.logging import logger

__all__ = [
    'AuthenticationService',
    'AuthorizationService',
    'setup'
]

async def setup(bot):
    """Central initialization of the Authentication and Authorization services"""
    try:
        # Initialize authentication service
        auth_service = AuthenticationService(bot)
        bot.authentication = auth_service
        
        # Initialize authorization service
        authorization_service = AuthorizationService(bot)
        bot.authorization = authorization_service
        
        logger.info("Authentication and Authorization services initialized successfully")
        return {
            'authentication': auth_service,
            'authorization': authorization_service
        }
    except Exception as e:
        logger.error(f"Failed to initialize auth services: {e}")
        raise

## You can now use:
#from core.services.auth import AuthenticationService, AuthorizationService