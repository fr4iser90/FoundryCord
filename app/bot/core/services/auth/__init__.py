from .auth_service import AuthService
from .auth_commands import AuthCommands
from core.services.logging.logging_commands import logger

__all__ = ['AuthService', 'AuthCommands']

async def setup(bot):
    """Central initialization of the Auth service"""
    try:
        # Initialize auth service
        auth_service = AuthService(bot)
        bot.auth = auth_service
        
        # Einfach direkt als Cog hinzufügen
        commands = AuthCommands(bot, auth_service)
        bot.add_cog(commands)
        
        logger.info("Auth service and commands initialized successfully")
        return auth_service
    except Exception as e:
        logger.error(f"Failed to initialize auth service: {e}")
        raise