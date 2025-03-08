from infrastructure.logging import logger
from infrastructure.config.channels.game_server_config import GameServerChannelConfig

class GameServerChannelService:
    def __init__(self, channel_setup_service):
        self.channel_setup = channel_setup_service
        
    async def setup_minecraft_channels(self, server_id: str, server_name: str) -> bool:
        """Sets up channels for a Minecraft server"""
        logger.info(f"Setting up channels for Minecraft server {server_id} ({server_name})")
        
        config = GameServerChannelConfig.get_minecraft_config(server_id, server_name)
        await self.channel_setup.register_gameserver_channels(server_id, config)
        return True