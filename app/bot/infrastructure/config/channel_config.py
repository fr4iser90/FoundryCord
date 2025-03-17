"""Channel configuration module for Discord channels."""
from typing import Dict, Optional, List
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

# Core imports
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from nextcord import TextChannel

# Import constants directly (move any complex imports to function level)
from app.bot.infrastructure.config.constants.channel_constants import CHANNELS
from app.bot.infrastructure.config.constants.dashboard_constants import DASHBOARD_MAPPINGS

# Fix import to use the correct model location
from app.shared.infrastructure.database.management.connection import get_session

# Import ChannelMapping explizit hier
from app.shared.infrastructure.database.models import ChannelMapping, AutoThreadChannel

class ChannelConfig:
    """Channel configuration for Discord channels."""
    
    # Constants
    CHANNELS = CHANNELS
    DASHBOARD_MAPPINGS = DASHBOARD_MAPPINGS
    DISCORD_SERVER = None
    
    @staticmethod
    def register(bot) -> Dict:
        """Register channel configuration with the bot."""
        
        async def setup(bot):
            try:
                logger.info("Setting up Discord channels")
                
                # Import here to avoid circular imports
                from app.bot.infrastructure.discord.channel_setup_service import ChannelSetupService
                
                # Create channel setup service
                channel_setup = ChannelSetupService(bot)
                await channel_setup.initialize()
                
                # Setup channels
                channels = {}
                for channel_name, config in CHANNELS.items():
                    try:
                        channel = await channel_setup.ensure_channel_exists(channel_name)
                        if channel:
                            channels[channel_name] = channel
                    except Exception as e:
                        logger.error(f"Error creating channel {channel_name}: {e}")
                
                logger.info(f"Created {len(channels)} channels")
                return channels
                
            except Exception as e:
                logger.error(f"Failed to setup channels: {e}")
                return {}
                
        return {
            "name": "Channels",
            "setup": setup
        }

    # Additional methods can be moved to implementation-specific functions or 
    # to separate class methods that defer imports to function level

    @classmethod
    async def create_channel_setup(cls, bot) -> 'ChannelSetupService':
        """Creates and configures the channel setup service"""
        try:
            cls.DISCORD_SERVER = bot.env_config.guild_id
            
            # Load existing channel mappings from database
            async for session in get_session():
                result = await session.execute(select(ChannelMapping))
                mappings = result.scalars().all()
                logger.info(f"Found {len(mappings)} channel mappings in database")
                await cls._initialize_channel_mappings(session, mappings)
            
            # Import here to avoid circular imports
            from app.bot.infrastructure.discord.channel_setup_service import ChannelSetupService
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
    async def get_channel_factory_config(cls, channel_name: str, guild, category_id: int) -> Dict:
        """Creates configuration for channel factory"""
        channel_config = cls.CHANNELS.get(channel_name, {})
        return {
            'guild': guild,
            'name': channel_name,
            'category_id': category_id,  # Now passed as parameter
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
            
            # Get channel config
            channel_config = cls.CHANNELS.get(channel_name, {})
            if not channel_config:
                logger.error(f"No configuration found for channel {channel_name}")
                return False
            
            # Find which category this channel belongs to
            category_type = None
            for cat_type, channels in CATEGORY_CHANNEL_MAPPINGS.items():
                if channel_name in channels:
                    category_type = cat_type
                    break
                
            if not category_type:
                logger.error(f"Channel {channel_name} not found in any category mapping")
                return False
            
            # Look for category setup service with correct attribute name
            # Try several possible service attribute names based on lifecycle manager's naming convention
            possible_service_attrs = [
                'category_setup',
                'category_setup_service',
                'category_service',
                'category'
            ]
            
            category_setup = None
            for attr in possible_service_attrs:
                if hasattr(bot, attr) and hasattr(getattr(bot, attr), 'get_category'):
                    category_setup = getattr(bot, attr)
                    logger.info(f"Found category service as bot.{attr}")
                    break
                
            if not category_setup:
                # Check components if available
                if hasattr(bot, 'components') and isinstance(bot.components, dict):
                    component_names = ['Category Setup', 'CategorySetup', 'Category']
                    for name in component_names:
                        if name in bot.components and hasattr(bot.components[name], 'get_category'):
                            category_setup = bot.components[name]
                            logger.info(f"Found category service in components as '{name}'")
                            break
            
            if not category_setup:
                # Last resort - try to create a temporary instance if possible
                try:
                    logger.warning("No category service found - creating temporary instance")
                    from app.bot.infrastructure.discord.category_setup_service import CategorySetupService
                    temp_service = CategorySetupService(bot)
                    await temp_service.initialize()
                    category_setup = temp_service
                except Exception as e:
                    logger.error(f"Failed to create temporary category service: {e}")
                    return False
                
            # Get the category
            category = await category_setup.get_category(category_type)
            if not category:
                # Try to ensure it exists
                logger.info(f"Category {category_type} not found, trying to create it")
                category = await category_setup.ensure_category_exists(category_type)
                
            if not category:
                logger.error(f"Failed to get or create category {category_type}")
                return False
            
            guild = bot.guilds[0] if bot.guilds else None
            if not guild:
                logger.error("No guild available to recreate channel")
                return False
            
            # Create channel through factory - using the CORRECT parameter name
            try:
                # Check if component_factory is available and has channel factory
                if hasattr(bot, 'component_factory') and 'channel' in bot.component_factory.factories:
                    channel_factory = bot.component_factory.factories['channel']
                else:
                    # Try to create a temporary channel factory
                    from app.bot.infrastructure.factories.discord import ChannelFactory
                    channel_factory = ChannelFactory(bot)
                    
                new_channel = await channel_factory.create_channel(
                    guild=guild,
                    name=channel_name,
                    category_id=category.id,  # CORRECT parameter as used in channel_setup_service.py
                    is_private=channel_config.get('is_private', False),
                    topic=channel_config.get('topic', None),
                    slowmode=channel_config.get('slowmode', 0)
                )
                
                if new_channel:
                    await cls.set_channel_id(channel_name, new_channel.id)
                    logger.info(f"Successfully repaired channel {channel_name}")
                    return True
                else:
                    logger.error(f"Failed to create channel {channel_name}")
                    return False
                
            except Exception as e:
                logger.error(f"Error creating channel: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Error repairing channel mapping: {e}")
            return False 
