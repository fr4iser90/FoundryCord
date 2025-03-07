from services.auth import AuthenticationService , AuthorizationService
from .auth_commands import AuthCommands
from infrastructure.logging import logger

__all__ = ['AuthCommands', 'setup']

async def setup(bot):
    """Central initialization of the Auth commands"""
    try:
        # Check if authentication and authorization services are already initialized
        if not hasattr(bot, 'authentication') or not hasattr(bot, 'authorization'):
            logger.warning("Auth services not found on bot instance. They should be initialized before commands.")
            # Initialize them if needed (fallback, not ideal for DDD)
            from app.bot.services.auth import setup as setup_services
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