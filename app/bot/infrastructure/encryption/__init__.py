from .encryption_service import EncryptionService
from .encryption_commands import EncryptionCommands
from infrastructure.logging import logger

__all__ = ['EncryptionService', 'EncryptionCommands']

async def setup(bot):
    """Central initialization of the Encryption service"""
    try:
        # Initialize encryption service
        encryption_service = EncryptionService(bot)
        await encryption_service.initialize()  # Make sure to wait for initialization
        bot.encryption = encryption_service
        
        # Initialize commands with service instance
        commands = EncryptionCommands(bot, encryption_service)
        bot.add_cog(commands)
        
        logger.info("Encryption service and commands initialized successfully")
        return encryption_service
    except Exception as e:
        logger.error(f"Failed to initialize encryption service: {e}")
        raise