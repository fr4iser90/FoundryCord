from app.shared.database.migrations.init_db import init_db
from .channel_setup_service import ChannelSetupService
from .game_server_channels import setup_minecraft_channels
from app.shared.logging import logger

async def setup_discord_channels(bot):
    """Setup function for Discord channels"""
    try:
        # 1. Erst Datenbank initialisieren
        await init_db()
        logger.info("Database tables created")
        
        # 2. Dann Channel Setup Service erstellen
        if not hasattr(bot, 'channel_setup'):
            logger.info("Creating new ChannelSetupService")
            bot.channel_setup = ChannelSetupService(bot)
        
        # 3. Service initialisieren wenn Bot ready
        if bot.is_ready():
            await bot.channel_setup.initialize()
            
        logger.info("Discord channel setup service registered")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing Discord channel setup: {e}")
        return False
