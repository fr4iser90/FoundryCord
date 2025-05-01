import nextcord
import logging
from typing import Dict, List, Optional, Any
from app.shared.domain.repositories.discord.channel_repository import ChannelRepository
from app.shared.domain.repositories.discord.category_repository import CategoryRepository
from app.bot.application.services.channel.channel_builder import ChannelBuilder
from app.shared.infrastructure.models.discord.entities.channel_entity import ChannelEntity
from app.shared.infrastructure.models.discord.enums.channels import ChannelType
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.repositories.discord.channel_repository_impl import ChannelRepositoryImpl
from app.shared.infrastructure.repositories.discord.category_repository_impl import CategoryRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_bot_logger()

class ChannelSetupService:
    """Service for managing Discord channel setup and synchronization"""
    
    def __init__(self, channel_builder: ChannelBuilder):
        """Initialize the channel setup service."""
        self.channel_builder = channel_builder
    
    async def initialize(self):
        """Initialize the channel setup service."""
        logger.info("Initializing channel setup service")
        # The initialization is now handled in ChannelWorkflow.initialize()
        # to avoid direct ORM queries that might fail
        return True
    
    async def setup_channels(self, guild: nextcord.Guild, session: AsyncSession) -> Dict[str, nextcord.abc.GuildChannel]:
        """
        Set up all channels for the guild and return a mapping of channel names to Discord channels
        """
        logger.info(f"Setting up channels for guild: {guild.name}")
        
        channel_repo = ChannelRepositoryImpl(session)
        category_repo = CategoryRepositoryImpl(session)
        
        category_map = {cat.name: cat for cat in guild.categories}
        
        channel_map = await self.channel_builder.setup_all_channels(guild, category_map, session)
        
        logger.info(f"Successfully set up {len(channel_map)} channels")
        return channel_map
    
    async def sync_with_discord(self, guild: nextcord.Guild, session: AsyncSession) -> None:
        """
        Synchronize database channels with existing Discord channels
        """
        logger.info(f"Syncing channels with Discord for guild: {guild.name}")
        await self.channel_builder.sync_channels(guild, session)
        logger.info("Channel synchronization completed")
    
    async def get_channel_by_name(self, name: str, session: AsyncSession) -> Optional[ChannelEntity]:
        """
        Get a channel model by name from database
        """
        channel_repo = ChannelRepositoryImpl(session)
        
        all_channels = await channel_repo.get_all_channels()
        matching_channels = [c for c in all_channels if c.name == name]
        
        if matching_channels:
            channel = matching_channels[0]
            return channel
        
        return None
    
    async def get_channels_by_type(self, channel_type: ChannelType, session: AsyncSession) -> List[ChannelEntity]:
        """
        Get all channels of a specific type
        """
        channel_repo = ChannelRepositoryImpl(session)
        
        result = await session.execute(select(ChannelEntity).where(ChannelEntity.type == channel_type.value))
        return result.scalars().all()
    
    async def get_channels_by_category(self, category_name: str, session: AsyncSession) -> List[ChannelEntity]:
        """
        Get all channels in a specific category
        """
        category_repo = CategoryRepositoryImpl(session)
        channel_repo = ChannelRepositoryImpl(session)
        
        cat_result = await session.execute(select(CategoryEntity).where(CategoryEntity.name == category_name))
        category = cat_result.scalars().first()
        if not category:
            return []
        
        chan_result = await session.execute(select(ChannelEntity).where(ChannelEntity.category_id == category.id))
        return chan_result.scalars().all()
    
    async def create_text_channel(self, guild: nextcord.Guild, name: str, category_name: str, 
                               session: AsyncSession, topic: str = None, position: int = 0) -> Optional[nextcord.TextChannel]:
        """
        Helper method to create a text channel with default settings
        """
        category_repo = CategoryRepositoryImpl(session)
        channel_repo = ChannelRepositoryImpl(session)
        
        cat_result = await session.execute(select(CategoryEntity).where(CategoryEntity.name == category_name))
        category = cat_result.scalars().first()
        if not category:
            logger.error(f"Category not found: {category_name}")
            return None
        
        channel_model = ChannelEntity(
            name=name,
            category_id=category.id,
            category_discord_id=category.discord_id,
            type=ChannelType.TEXT,
            position=position,
            topic=topic
        )
        
        saved_channel = await channel_repo.save_channel(channel_model)
        
        discord_channel = await self.channel_builder.create_channel(guild, saved_channel, session)
        return discord_channel
    
    async def create_voice_channel(self, guild: nextcord.Guild, name: str, category_name: str, 
                                session: AsyncSession, position: int = 0) -> Optional[nextcord.VoiceChannel]:
        """
        Helper method to create a voice channel with default settings
        """
        category_repo = CategoryRepositoryImpl(session)
        channel_repo = ChannelRepositoryImpl(session)
        
        cat_result = await session.execute(select(CategoryEntity).where(CategoryEntity.name == category_name))
        category = cat_result.scalars().first()
        if not category:
            logger.error(f"Category not found: {category_name}")
            return None
        
        channel_model = ChannelEntity(
            name=name,
            category_id=category.id,
            category_discord_id=category.discord_id,
            type=ChannelType.VOICE,
            position=position
        )
        
        saved_channel = await channel_repo.save_channel(channel_model)
        
        discord_channel = await self.channel_builder.create_channel(guild, saved_channel, session)
        return discord_channel 