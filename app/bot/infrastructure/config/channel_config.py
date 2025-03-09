from typing import Dict, Optional, List
from infrastructure.logging import logger
from nextcord import TextChannel
from infrastructure.discord.channel_setup_service import ChannelSetupService
from infrastructure.database.models import ChannelMapping
from infrastructure.database.models.config import get_session
from infrastructure.config.constants.channel_constants import CHANNELS
from infrastructure.config.constants.dashboard_constants import DASHBOARD_MAPPINGS
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

class ChannelConfig:
    # Konstanten aus channel_constants.py als Klassenattribute
    CHANNELS = CHANNELS
    DASHBOARD_MAPPINGS = DASHBOARD_MAPPINGS
    
    # Channel IDs werden aus EnvConfig geladen
    HOMELAB_CATEGORY_ID = None
    DISCORD_SERVER = None
    
    @classmethod
    async def create_channel_setup(cls, bot) -> 'ChannelSetupService':
        """Creates and configures the channel setup service"""
        try:
            # Load from bot.env_config
            cls.HOMELAB_CATEGORY_ID = bot.env_config.HOMELAB_CATEGORY_ID
            cls.DISCORD_SERVER = bot.env_config.guild_id
            
            # Import hier um zirkuläre Imports zu vermeiden
            from infrastructure.discord.channel_setup_service import ChannelSetupService
            
            # Load existing channel mappings from database
            async for session in get_session():
                result = await session.execute(select(ChannelMapping))
                mappings = result.scalars().all()
                logger.info(f"Found {len(mappings)} channel mappings in database")
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
            'welcome': await cls.get_channel_id('welcome'),
            'projects': await cls.get_channel_id('projects'),
            'monitoring': await cls.get_channel_id('monitoring'),
            # Weitere Dashboard-Kanäle hier hinzufügen
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

    @classmethod
    async def setup_channel_dashboards(cls, bot) -> None:
        """Creates/updates dashboards for all channels"""
        for channel_name, dashboard_config in cls.DASHBOARD_MAPPINGS.items():
            if dashboard_config['auto_create']:
                channel_id = await cls.get_channel_id(channel_name)
                if channel_id:
                    try:
                        dashboard = await bot.dashboard_factory.create(
                            dashboard_config['dashboard_type'],
                            channel_id=channel_id,
                            refresh_interval=dashboard_config['refresh_interval']
                        )
                        if dashboard:
                            await dashboard['dashboard'].setup()
                    except Exception as e:
                        logger.error(f"Failed to setup dashboard for {channel_name}: {e}")

    @classmethod
    async def validate_channel_id(cls, channel_name: str, bot) -> bool:
        """Validates if a channel ID exists and is accessible"""
        try:
            channel_id = await cls.get_channel_id(channel_name)
            if not channel_id:
                return False
                
            channel = bot.get_channel(channel_id)
            return channel is not None
        except Exception as e:
            logger.error(f"Error validating channel {channel_name}: {e}")
            return False

    @classmethod
    async def repair_channel_mapping(cls, channel_name: str, bot) -> bool:
        """Attempts to repair a channel mapping if the channel doesn't exist"""
        try:
            logger.info(f"Attempting to repair channel mapping for {channel_name}")
            channel_id = await cls.get_channel_id(channel_name)
            
            # Get channel config
            channel_config = cls.CHANNELS.get(channel_name, {})
            if not channel_config:
                logger.error(f"No configuration found for channel {channel_name}")
                return False
            
            # Create channel through factory
            channel_factory = bot.component_factory.factories['channel']
            guild = bot.guilds[0] if bot.guilds else None
            if not guild:
                logger.error("No guild available to recreate channel")
                return False
            
            new_channel = await channel_factory.create_channel(
                guild=guild,
                name=channel_name,
                is_private=channel_config.get('is_private', False),
                topic=channel_config.get('topic', None),
                slowmode=channel_config.get('slowmode', 0)
            )
            
            return new_channel is not None
        except Exception as e:
            logger.error(f"Error repairing channel mapping: {e}")
            return False 
