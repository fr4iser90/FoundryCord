# Remove the direct imports and use lazy imports
__all__ = ['EncryptionService', 'EncryptionCommands', 'KeyManagementService']

def get_encryption_service():
    from .encryption_service import EncryptionService
    return EncryptionService

def get_encryption_commands():
    from .encryption_commands import EncryptionCommands
    return EncryptionCommands

def get_key_management_service():
    from .key_management_service import KeyManagementService
    return KeyManagementService

async def setup(bot):
    """Initialize encryption components"""
    from app.shared.logging import logger
    try:
        encryption_service = get_encryption_service()(bot)
        commands = get_encryption_commands()(bot, encryption_service)
        await encryption_service.initialize()
        bot.add_cog(commands)
        
        logger.info("Encryption service and commands initialized successfully")
        return encryption_service
    except Exception as e:
        logger.error(f"Failed to initialize encryption service: {e}")
        raise