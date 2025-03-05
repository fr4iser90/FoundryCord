from typing import Dict, List, Optional
import nextcord
from core.services.logging.logging_commands import logger

class ChannelSetupService:
    def __init__(self, bot):
        self.bot = bot
        # Nur die Core-Channels, die der Bot für seine Grundfunktionen braucht
        self.required_channels = {
            # Allgemeine Channels
            'general': {
                'name': 'general',
                'topic': 'General Information',
                'is_private': False
            },
            'gameservers': {
                'name': 'gameservers',
                'topic': 'Gameserver Overview',
                'is_private': False,
                'threads': [
                    {'name': 'status-overview', 'is_private': False},
                    {'name': 'announcements', 'is_private': False}
                ]
            },
            'services': {
                'name': 'services',
                'topic': 'Service Overview',
                'is_private': True,
                'threads': [
                    {'name': 'status', 'is_private': True},
                    {'name': 'maintenance', 'is_private': True}
                ]
            },
            'infrastructure': {
                'name': 'infrastructure',
                'topic': 'Infrastructure Management',
                'is_private': True,
                'threads': [
                    {'name': 'network', 'is_private': True},
                    {'name': 'hardware', 'is_private': True},
                    {'name': 'updates', 'is_private': True}
                ]
            },
            'projects': {
                'name': 'projects',
                'topic': 'Project Management',
                'is_private': True,
                'threads': [
                    {'name': 'planning', 'is_private': True},
                    {'name': 'tasks', 'is_private': True}
                ]
            },
            'backups': {
                'name': 'backups',
                'topic': 'Backup Management',
                'is_private': True,
                'threads': [
                    {'name': 'schedule', 'is_private': True},
                    {'name': 'logs', 'is_private': True},
                    {'name': 'status', 'is_private': True}
                ]
            },
            'server-management': {
                'name': 'server-management',
                'topic': 'Server Administration',
                'is_private': True,
                'threads': [
                    {'name': 'commands', 'is_private': True},
                    {'name': 'updates', 'is_private': True},
                    {'name': 'maintenance', 'is_private': True}
                ]
            },
            'logs': {
                'name': 'logs',
                'topic': 'System Logs',
                'is_private': True,
                'threads': [
                    {'name': 'system-logs', 'is_private': True},
                    {'name': 'error-logs', 'is_private': True},
                    {'name': 'access-logs', 'is_private': True}
                ]
            },
            'monitoring': {
                'name': 'monitoring',
                'topic': 'System Monitoring',
                'is_private': True,
                'threads': [
                    {'name': 'system-status', 'is_private': False},
                    {'name': 'performance', 'is_private': True},
                    {'name': 'alerts', 'is_private': True}
                ]
            },
            'bot-control': {
                'name': 'bot-control',
                'topic': 'Bot Management',
                'is_private': True,
                'threads': [
                    {'name': 'commands', 'is_private': True},
                    {'name': 'logs', 'is_private': True},
                    {'name': 'updates', 'is_private': True}
                ]
            },
            'alerts': {
                'name': 'alerts',
                'topic': 'System Alerts',
                'is_private': True,
                'threads': [
                    {'name': 'critical', 'is_private': True},
                    {'name': 'warnings', 'is_private': True},
                    {'name': 'notifications', 'is_private': True}
                ]
            }
        }

    def register_gameserver_channels(self, server_id: str, config: Dict):
        """Registriert Channels für einen Gameserver"""
        self.required_channels[f'gameserver-{server_id}'] = config
        logger.info(f"Registered channels for gameserver {server_id}")

    async def setup(self):
        """Initialer Setup aller benötigten Channels"""
        logger.info("Starting channel setup...")
        
        for channel_id, config in self.required_channels.items():
            try:
                channel = await self.bot.channel_factory.get_or_create_channel(
                    self.bot.guild,
                    config['name'],
                    category_id=config['category_id'],
                    is_private=config.get('is_private', False),
                    topic=config.get('topic')
                )
                
                if 'threads' in config:
                    for thread_config in config['threads']:
                        await self.bot.thread_factory.get_or_create_thread(
                            channel,
                            thread_config['name'],
                            is_private=thread_config.get('is_private', False),
                            auto_archive_duration=thread_config.get('auto_archive_duration', 1440),
                            reason="Automatic setup"
                        )
                
                logger.info(f"Channel {config['name']} setup completed")
                
            except Exception as e:
                logger.error(f"Error setting up channel {config['name']}: {str(e)}")