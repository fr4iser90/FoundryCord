from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.shared.infrastructure.models.discord.entities.channel_entity import ChannelEntity, ChannelPermissionEntity
from app.shared.infrastructure.models.discord.mappings.channel_mapping import ChannelMapping
from app.shared.domain.repositories.discord.channel_repository import ChannelRepository
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from app.shared.infrastructure.database.api import get_session
from app.shared.infrastructure.database.session.context import session_context
import logging

logger = logging.getLogger("homelab.db")


class ChannelRepositoryImpl(BaseRepositoryImpl[ChannelEntity], ChannelRepository):
    """Implementation of the Channel repository"""
    
    def __init__(self, session_or_service=None):
        """Initialize the repository with a session or database service"""
        if not isinstance(session_or_service, AsyncSession):
             raise ValueError("AsyncSession must be provided to ChannelRepositoryImpl")
        super().__init__(ChannelEntity, session_or_service)
    
    def _entity_to_mapping(self, entity: ChannelEntity) -> ChannelMapping:
        """Convert a database entity to a mapping"""
        return ChannelMapping(
            guild_id=str(entity.guild_id) if entity.guild_id else None,
            channel_id=str(entity.discord_id) if entity.discord_id else None,
            channel_name=entity.name,
            channel_type=entity.type.value,
            parent_channel_id=str(entity.category_discord_id) if entity.category_discord_id else None,
            enabled=entity.is_enabled
        )
    
    def _mapping_to_entity(self, mapping: ChannelMapping) -> ChannelEntity:
        """Convert a mapping to a database entity"""
        return ChannelEntity(
            name=mapping.channel_name,
            discord_id=int(mapping.channel_id) if mapping.channel_id else None,
            type=mapping.channel_type,
            is_enabled=mapping.enabled,
            category_discord_id=int(mapping.parent_channel_id) if mapping.parent_channel_id else None
        )
    
    async def get_all_channels(self) -> List[ChannelEntity]:
        """Get all channels from the database"""
        try:
            result = await self.session.execute(
                select(self.model)
            )
            channels = result.scalars().all()
            
            return list(channels)
        except Exception as e:
             logger.error(f"Error getting all channels: {e}", exc_info=True)
             return []
    
    async def get_channel_by_id(self, channel_id: int) -> Optional[ChannelEntity]:
        """Get a channel by its database ID"""
        try:
            channel = await self.session.get(self.model, channel_id)
            return channel
        except Exception as e:
             logger.error(f"Error getting channel by id {channel_id}: {e}", exc_info=True)
             return None
    
    async def get_channel_by_discord_id(self, discord_id: int) -> Optional[ChannelEntity]:
        """Get a channel by its Discord ID"""
        try:
            result = await self.session.execute(
                select(self.model).where(self.model.discord_id == discord_id)
            )
            channel = result.scalar_one_or_none()
            return channel
        except Exception as e:
             logger.error(f"Error getting channel by discord_id {discord_id}: {e}", exc_info=True)
             return None
    
    async def get_channel_by_name_and_category(self, name: str, category_id: int) -> Optional[ChannelEntity]:
        """Get a channel by its name and category ID"""
        try:
            result = await self.session.execute(
                select(self.model)
                .options(selectinload(self.model.permissions))
                .filter(self.model.name == name, self.model.category_id == category_id)
            )
            channel = result.scalars().first()
            if channel:
                return channel
            return None
        except Exception as e:
             logger.error(f"Error getting channel by name and category: {e}", exc_info=True)
             return None
    
    async def get_channels_by_category_id(self, category_id: int) -> List[ChannelEntity]:
        """Get all channels in a specific category"""
        try:
            channels = await self.session.execute(
                select(self.model)
                .filter(self.model.category_id == category_id)
            )
            channels = channels.scalars().all()
            return list(channels)
        except Exception as e:
             logger.error(f"Error getting channels by category id: {e}", exc_info=True)
             return []
    
    async def get_channels_by_category_discord_id(self, category_discord_id: int) -> List[ChannelEntity]:
        """Get all channels in a specific Discord category"""
        try:
            channels = await self.session.execute(
                select(self.model)
                .filter(self.model.category_discord_id == category_discord_id)
            )
            channels = channels.scalars().all()
            return list(channels)
        except Exception as e:
             logger.error(f"Error getting channels by category discord id: {e}", exc_info=True)
             return []
    
    async def save_channel(self, channel: ChannelEntity) -> ChannelEntity:
        """Save a channel to the database (create or update)"""
        try:
            self.session.add(channel)
            await self.session.flush()
            await self.session.refresh(channel)
            return channel
        except Exception as e:
             logger.error(f"Error saving channel {getattr(channel, 'id', 'N/A')}: {e}", exc_info=True)
             await self.session.rollback()
             raise
    
    async def update_discord_id(self, channel_id: int, discord_id: int) -> bool:
        """Update the Discord ID of a channel after it's created in Discord"""
        try:
            channel = await self.session.get(self.model, channel_id)
            if channel:
                channel.discord_id = discord_id
                channel.is_created = True
                await self.session.commit()
                return True
            return False
        except Exception as e:
             logger.error(f"Error updating discord id: {e}", exc_info=True)
             await self.session.rollback()
             return False
    
    async def update_channel_status(self, channel_id: int, is_created: bool) -> bool:
        """Update the creation status of a channel"""
        try:
            channel = await self.session.get(self.model, channel_id)
            if channel:
                channel.is_created = is_created
                await self.session.commit()
                return True
            return False
        except Exception as e:
             logger.error(f"Error updating channel status: {e}", exc_info=True)
             await self.session.rollback()
             return False
    
    async def delete_channel(self, channel_id: int) -> bool:
        """Delete a channel from the database by ID."""
        try:
            channel = await self.session.get(self.model, channel_id)
            if channel:
                await super().delete(channel)
                return True
            return False
        except Exception as e:
             logger.error(f"Error deleting channel id {channel_id}: {e}", exc_info=True)
             await self.session.rollback()
             return False
    
    async def create_from_template(self, template: ChannelEntity, category_id: Optional[int] = None, 
                                 category_discord_id: Optional[int] = None) -> ChannelEntity:
        """Create a new channel from a template"""
        try:
            new_channel = ChannelEntity(
                name=template.name,
                type=template.type,
                description=template.description,
                category_id=category_id,
                category_discord_id=category_discord_id,
                position=template.position,
                permission_level=template.permission_level,
                is_enabled=True,
                is_created=False,
                nsfw=template.nsfw,
                slowmode_delay=template.slowmode_delay,
                topic=template.topic,
                thread_config=template.thread_config,
                metadata_json=template.metadata_json
            )
            self.session.add(new_channel)
            await self.session.commit()
            return new_channel
        except Exception as e:
            logger.error(f"Error creating channel from template: {e}")
            raise
    
    async def get_enabled_channels(self) -> List[ChannelEntity]:
        """Get all enabled channels"""
        try:
            channels = await self.session.execute(
                select(self.model)
                .filter(self.model.is_enabled == True)
            )
            channels = channels.scalars().all()
            return list(channels)
        except Exception as e:
             logger.error(f"Error getting enabled channels: {e}", exc_info=True)
             return []
    
    async def get_channels_by_type(self, channel_type: str) -> List[ChannelEntity]:
        """Get all channels of a specific type"""
        try:
            channels = await self.session.execute(
                select(self.model)
                .filter(self.model.type == channel_type)
            )
            channels = channels.scalars().all()
            return list(channels)
        except Exception as e:
             logger.error(f"Error getting channels by type: {e}", exc_info=True)
             return []
    
    async def get_channel_mapping(self) -> Dict[str, ChannelEntity]:
        """Get a mapping of channel names to channel models"""
        try:
            channels = await self.get_all_channels()
            return {channel.name: channel for channel in channels}
        except Exception as e:
             logger.error(f"Error getting channel mapping: {e}", exc_info=True)
             return {}

    async def create_channel(self, channel: ChannelEntity) -> ChannelEntity:
        """Create a new channel. Assumes input 'channel' has necessary data but maybe not ID."""
        try:
            self.session.add(channel)
            await self.session.flush()
            await self.session.refresh(channel)
            
            if hasattr(channel, 'permissions') and channel.permissions:
                 for permission_data in channel.permissions:
                      perm_entity = ChannelPermissionEntity(
                           channel_id=channel.id,
                           role_id=getattr(permission_data, 'role_id', None),
                      )
                      self.session.add(perm_entity)
                 await self.session.flush()

            return channel
        except Exception as e:
             logger.error(f"Error in create_channel: {e}", exc_info=True)
             await self.session.rollback()
             raise