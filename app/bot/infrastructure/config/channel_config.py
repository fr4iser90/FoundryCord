from typing import Dict, Optional, List
from infrastructure.logging import logger
from nextcord import TextChannel
from infrastructure.discord.channel_setup_service import ChannelSetupService
from infrastructure.database.models.models import ChannelMapping
from infrastructure.database.models.config import get_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


class ChannelConfig:
    # Channel IDs werden aus EnvConfig geladen
    HOMELAB_CATEGORY_ID = None
    SERVER_ID = None
    
    # Channel-Struktur
    CHANNELS = {
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
                    {'name': 'tasks', 'is_private': True},
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
    
    @classmethod
    async def create_channel_setup(cls, bot) -> ChannelSetupService:
        """Creates and configures the channel setup service"""
        try:
            # Load from bot.env_config
            cls.HOMELAB_CATEGORY_ID = bot.env_config.HOMELAB_CATEGORY_ID
            cls.SERVER_ID = bot.env_config.guild_id
            
            # Load existing channel mappings from database
            async for session in get_session():
                # Get all existing mappings
                result = await session.execute(select(ChannelMapping))
                mappings = result.scalars().all()
                
                # Log found mappings
                logger.info(f"Found {len(mappings)} channel mappings in database")
                
                # Initialize any missing channels in database
                await cls._initialize_channel_mappings(session, mappings)
            
            channel_setup = ChannelSetupService(bot)
            return channel_setup
            
        except Exception as e:
            logger.error(f"Failed to create channel setup: {e}")
            raise

    @classmethod
    async def _initialize_channel_mappings(cls, session: AsyncSession, existing_mappings: List[ChannelMapping]):
        """Initialize missing channel mappings in database"""
        try:
            for channel_name, config in cls.CHANNELS.items():
                # Check main channel
                if not any(m.channel_name == channel_name for m in existing_mappings):
                    logger.info(f"Initializing mapping for channel: {channel_name}")
                    new_mapping = ChannelMapping(
                        channel_name=channel_name,
                        channel_id=None,  # Will be set when channel is created
                        created_at=datetime.utcnow()
                    )
                    session.add(new_mapping)
                
                # Check thread channels
                if 'threads' in config:
                    for thread in config['threads']:
                        thread_name = f"{channel_name}.{thread['name']}"
                        if not any(m.channel_name == thread_name for m in existing_mappings):
                            logger.info(f"Initializing mapping for thread: {thread_name}")
                            new_mapping = ChannelMapping(
                                channel_name=thread_name,
                                channel_id=None,  # Will be set when thread is created
                                created_at=datetime.utcnow()
                            )
                            session.add(new_mapping)
            
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error initializing channel mappings: {e}")
            raise

    @classmethod
    async def set_channel_id(cls, channel_name: str, channel_id: int):
        """Stores the channel ID in the database"""
        try:
            async for session in get_session():
                # Check if mapping already exists
                stmt = select(ChannelMapping).where(ChannelMapping.channel_name == channel_name)
                result = await session.execute(stmt)
                mapping = result.scalar_one_or_none()
                
                if mapping:
                    mapping.channel_id = channel_id
                else:
                    mapping = ChannelMapping(
                        channel_name=channel_name,
                        channel_id=channel_id,
                        created_at=datetime.utcnow()
                    )
                    session.add(mapping)
                
                await session.commit()
                logger.debug(f"Channel ID saved successfully for {channel_name}")
        except Exception as e:
            logger.error(f"Error saving channel ID: {e}")
            raise

    @classmethod
    async def get_channel_id(cls, channel_name: str) -> Optional[int]:
        """Retrieves the channel ID from the database"""
        try:
            async for session in get_session():
                stmt = select(ChannelMapping).where(ChannelMapping.channel_name == channel_name)
                result = await session.execute(stmt)
                mapping = result.scalar_one_or_none()
                return mapping.channel_id if mapping else None
        except Exception as e:
            logger.error(f"Error retrieving channel ID: {e}")
            return None

    @classmethod
    async def get_dashboard_channels(cls) -> Dict[str, Optional[int]]:
        """Returns IDs of all dashboard-relevant channels"""
        return {
            'project_dashboard': await cls.get_channel_id('projects'),
        }

    @classmethod
    async def validate_channels(cls) -> List[str]:
        """Validates if all required channel IDs exist"""
        missing_channels = []
        
        for channel_name, config in cls.CHANNELS.items():
            if not await cls.get_channel_id(channel_name):
                missing_channels.append(channel_name)
            
            if 'threads' in config:
                for thread in config['threads']:
                    thread_id = f"{channel_name}.{thread['name']}"
                    if not await cls.get_channel_id(thread_id):
                        missing_channels.append(thread_id)
        
        return missing_channels

    @classmethod
    def get_channel_factory_config(cls, channel_name: str, guild) -> Dict:
        """Creates configuration for channel factory"""
        channel_config = cls.CHANNELS.get(channel_name, {})
        return {
            'guild': guild,
            'name': channel_name,
            'category_id': int(cls.HOMELAB_CATEGORY_ID),
            'is_private': channel_config.get('is_private', False),
            'topic': channel_config.get('topic'),
            'slowmode': channel_config.get('slowmode', 0)
        }
    
    @classmethod
    def get_thread_factory_config(cls, channel: TextChannel, thread_name: str) -> Dict:
        """Erstellt die Konfiguration für die ThreadFactory"""
        channel_name = channel.name
        channel_config = cls.CHANNELS.get(channel_name, {})
        thread_config = next(
            (t for t in channel_config.get('threads', []) if t['name'] == thread_name),
            {}
        )
        
        return {
            'channel': channel,
            'name': thread_name,
            'is_private': thread_config.get('is_private', False),
            'auto_archive_duration': thread_config.get('auto_archive_duration', 1440)
        }

    @staticmethod
    def register(bot) -> Dict:
        async def setup(bot):
            try:
                channel_setup = await ChannelConfig.create_channel_setup(bot)
                logger.info("Channel setup service created successfully")
                return channel_setup
            except Exception as e:
                logger.error(f"Failed to setup channel service: {e}")
                raise
                
        return {
            "name": "Channel Setup",
            "setup": setup
        }