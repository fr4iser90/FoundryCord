from typing import Dict
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.application.services.channel.channel_setup_service import ChannelSetupService

async def setup_minecraft_channels(channel_setup_service, server_id, server_name):
    """
    Registriert die Kanäle für einen Minecraft-Server
    """
    logger.info(f"Registering channels for Minecraft server {server_id} ({server_name})")
    
    # Konfiguration für den Minecraft-Server-Kanal
    channel_config = {
        'name': f'mc-{server_name}',
        'topic': f'Minecraft Server: {server_name}',
        'is_private': False,
        'threads': [
            {'name': 'status', 'is_private': False},
            {'name': 'console', 'is_private': True},
            {'name': 'backups', 'is_private': True},
            {'name': 'commands', 'is_private': True}
        ]
    }
    
    # Kanal beim Service registrieren
    channel_setup_service.register_gameserver_channels(server_id, channel_config)
    return True


