from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.config.constants.channel_constants import GameServerChannelConfig
from app.bot.application.services.channel.channel_setup_service import ChannelSetupService
from sqlalchemy.ext.asyncio import AsyncSession

class GameServerChannelService:
    def __init__(self):
        pass
        
    async def setup_minecraft_channels(self, server_id: str, server_name: str, session: AsyncSession) -> bool:
        """Sets up channels for a Minecraft server"""
        logger.info(f"Setting up channels for Minecraft server {server_id} ({server_name})")
        
        from app.bot.application.services.channel.channel_builder import ChannelBuilder
        channel_builder = ChannelBuilder()
        channel_setup_service = ChannelSetupService(channel_builder)

        category_name = "GAME SERVERS"
        channel_name = f"minecraft-{server_name.lower()}"
        try:
            await channel_setup_service.create_text_channel(
                guild=None,
                name=channel_name, 
                category_name=category_name, 
                session=session, 
                topic=f"Minecraft server {server_name}"
            )
            logger.warning("setup_minecraft_channels needs Guild object to create channels.")
            return False
        except Exception as e:
             logger.error(f"Error setting up Minecraft channels: {e}", exc_info=True)
             return False