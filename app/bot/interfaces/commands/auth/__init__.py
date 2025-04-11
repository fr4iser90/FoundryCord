from app.shared.domain.auth.services import AuthenticationService
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from .auth_commands import AuthCommands
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

__all__ = ['AuthCommands', 'setup']

def setup(bot):
    """Initialize auth commands"""
    key_service = KeyManagementService()
    auth_service = AuthenticationService(key_service)
    auth_service.initialize()
    bot.add_cog(AuthCommands(bot, auth_service))

async def setup_async(bot):
    """Central initialization of the Auth commands"""
    try:
        # Check if authentication and authorization services are already initialized
        if not hasattr(bot, 'authentication') or not hasattr(bot, 'authorization'):
            logger.warning("Auth services not found on bot instance. They should be initialized before commands.")
            # Initialize them if needed (fallback, not ideal for DDD)
            from app.shared.domain.auth import setup as setup_services
            await setup_services(bot)
        
        # Add commands as cog
        commands = AuthCommands(bot, bot.authentication, bot.authorization)
        
        # Use the lifecycle manager if available
        if hasattr(bot, 'lifecycle'):
            await bot.lifecycle.register_command(commands)
        else:
            bot.add_cog(commands)
        
        logger.info("Auth commands initialized successfully")
        return commands
    except Exception as e:
        logger.error(f"Failed to initialize auth commands: {e}")
        raise