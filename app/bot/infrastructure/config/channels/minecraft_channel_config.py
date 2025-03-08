from typing import Dict
from infrastructure.logging import logger

class MinecraftGameServerChannelConfig:
    @staticmethod
    def get_minecraft_config(server_id: str, server_name: str) -> Dict:
        return {
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