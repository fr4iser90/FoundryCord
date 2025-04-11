from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.shared.domain.services.wireguard.config_manager import WireguardConfigManager

class WireguardService:
    """Application service for WireGuard functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "/app/bot/database/wireguard"
        self.config_manager = WireguardConfigManager()
        self.commands_registered = False
        
    async def initialize(self):
        """Initialize the WireGuard service"""
        try:
            logger.info("Initializing WireGuard service")
            
            # Wait for encryption service to be available
            if not hasattr(self.bot, 'encryption'):
                import asyncio
                await asyncio.sleep(1)
            
            # Service is initialized but commands registered separately
            logger.info("WireGuard service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WireGuard service: {e}")
            raise
    
    def get_user_config(self, username):
        """Get configuration for a user"""
        return self.config_manager.get_user_config(self.config_path, username)
    
    def get_config_file_path(self, username):
        """Get the configuration file path for a user"""
        return self.config_manager.get_config_file_path(self.config_path, username)
    
    def get_qr_file_path(self, username):
        """Get the QR code file path for a user"""
        return self.config_manager.get_qr_file_path(self.config_path, username)
    
    def get_config_path(self):
        """Get the base configuration path"""
        return self.config_path

async def setup(bot):
    """Setup function for the WireGuard service"""
    service = WireguardService(bot)
    await service.initialize()
    return service