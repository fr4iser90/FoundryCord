from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.shared.infrastructure.models.discord.entities.channel_entity import ChannelEntity, ChannelPermissionEntity
from app.shared.infrastructure.models.discord.mappings.channel_mapping import ChannelMapping
from app.shared.domain.repositories.discord.channel_repository import ChannelRepository
from app.shared.infrastructure.database.api import get_session
from app.shared.infrastructure.database.session.context import session_context
import logging

logger = logging.getLogger("homelab.db")


class ChannelRepositoryImpl(ChannelRepository):
    """Implementation of the Channel repository"""
    
    def __init__(self, session_or_service=None):
        """Initialize the repository with a session or database service"""
        self.session_or_service = session_or_service
    
    async def _get_session(self) -> AsyncSession:
        """Get a session for database operations"""
        if isinstance(self.session_or_service, AsyncSession):
            return self.session_or_service
        else:
            # Get a session without using context manager to avoid state management issues
            from app.shared.infrastructure.database.api import get_session
            session_gen = get_session()
            session = await anext(session_gen)
            return session
    
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
        session = await self._get_session()
        try:
            # Use a simple query without eager loading to avoid the relationship issue
            result = await session.execute(
                select(ChannelEntity)
                # Remove the problematic eager loading for now
                # .options(selectinload(ChannelEntity.permissions))
            )
            channels = result.scalars().all()
            
            # Manually load permissions for each channel if needed
            for channel in channels:
                # Ensure permissions are loaded if they exist
                await session.refresh(channel, ["permissions"])
            
            return [self._entity_to_model(channel) for channel in channels]
        finally:
            # Only close if we created a new session
            if session != self.session_or_service:
                await session.close()
    
    async def get_channel_by_id(self, channel_id: int) -> Optional[ChannelEntity]:
        """Get a channel by its database ID"""
        session = await self._get_session()
        try:
            channel = await session.get(ChannelEntity, channel_id)
            return self._entity_to_model(channel) if channel else None
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def get_channel_by_discord_id(self, discord_id: int) -> Optional[ChannelEntity]:
        """Get a channel by its Discord ID"""
        session = await self._get_session()
        try:
            result = await session.execute(
                select(ChannelEntity).where(ChannelEntity.discord_id == discord_id)
            )
            channel = result.scalar_one_or_none()
            return self._entity_to_model(channel) if channel else None
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def get_channel_by_name_and_category(self, name: str, category_id: int) -> Optional[ChannelEntity]:
        """Get a channel by its name and category ID"""
        session = await self._get_session()
        try:
            result = await session.execute(
                select(ChannelEntity)
                .options(selectinload(ChannelEntity.permissions))
                .filter(ChannelEntity.name == name, ChannelEntity.category_id == category_id)
            )
            channel = result.scalars().first()
            if channel:
                return self._entity_to_model(channel)
            return None
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def get_channels_by_category_id(self, category_id: int) -> List[ChannelEntity]:
        """Get all channels in a specific category"""
        session = await self._get_session()
        try:
            channels = await session.execute(
                select(ChannelEntity)
                .filter(ChannelEntity.category_id == category_id)
            )
            channels = channels.scalars().all()
            return [self._entity_to_model(channel) for channel in channels]
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def get_channels_by_category_discord_id(self, category_discord_id: int) -> List[ChannelEntity]:
        """Get all channels in a specific Discord category"""
        session = await self._get_session()
        try:
            channels = await session.execute(
                select(ChannelEntity)
                .filter(ChannelEntity.category_discord_id == category_discord_id)
            )
            channels = channels.scalars().all()
            return [self._entity_to_model(channel) for channel in channels]
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def save_channel(self, channel: ChannelEntity) -> ChannelEntity:
        """Save a channel to the database (create or update)"""
        session = await self._get_session()
        try:
            async with session.begin():
                entity = self._model_to_entity(channel)
                session.add(entity)
                await session.flush()
                channel.id = entity.id
                return channel
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def update_discord_id(self, channel_id: int, discord_id: int) -> bool:
        """Update the Discord ID of a channel after it's created in Discord"""
        session = await self._get_session()
        try:
            channel = await session.get(ChannelEntity, channel_id)
            if channel:
                channel.discord_id = discord_id
                channel.is_created = True
                await session.commit()
                return True
            return False
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def update_channel_status(self, channel_id: int, is_created: bool) -> bool:
        """Update the creation status of a channel"""
        session = await self._get_session()
        try:
            channel = await session.get(ChannelEntity, channel_id)
            if channel:
                channel.is_created = is_created
                await session.commit()
                return True
            return False
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def delete_channel(self, channel_id: int) -> bool:
        """Delete a channel from the database"""
        session = await self._get_session()
        try:
            channel = await session.get(ChannelEntity, channel_id)
            if channel:
                await session.delete(channel)
                await session.commit()
                return True
            return False
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def create_from_template(self, template: ChannelEntity, category_id: Optional[int] = None, 
                                 category_discord_id: Optional[int] = None) -> ChannelEntity:
        """Create a new channel from a template"""
        session = self.session_or_service
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
            session.add(new_channel)
            await session.commit()
            return new_channel
        except Exception as e:
            logger.error(f"Error creating channel from template: {e}")
            raise
    
    async def get_enabled_channels(self) -> List[ChannelEntity]:
        """Get all enabled channels"""
        session = await self._get_session()
        try:
            channels = await session.execute(
                select(ChannelEntity)
                .filter(ChannelEntity.is_enabled == True)
            )
            channels = channels.scalars().all()
            return [self._entity_to_model(channel) for channel in channels]
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def get_channels_by_type(self, channel_type: str) -> List[ChannelEntity]:
        """Get all channels of a specific type"""
        session = await self._get_session()
        try:
            channels = await session.execute(
                select(ChannelEntity)
                .filter(ChannelEntity.type == channel_type)
            )
            channels = channels.scalars().all()
            return [self._entity_to_model(channel) for channel in channels]
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def get_channel_mapping(self) -> Dict[str, ChannelEntity]:
        """Get a mapping of channel names to channel models"""
        session = await self._get_session()
        try:
            channels = await self.get_all_channels()
            return {channel.name: channel for channel in channels}
        finally:
            if session != self.session_or_service:
                await session.close()

    async def create_channel(self, channel: ChannelEntity) -> ChannelEntity:
        """Create a new channel"""
        session = await self._get_session()
        try:
            async with session.begin():
                entity = ChannelEntity(
                    discord_id=channel.discord_id,
                    name=channel.name,
                    description=channel.description,
                    category_id=channel.category_id,
                    category_discord_id=channel.category_discord_id,
                    type=channel.type,
                    position=channel.position,
                    permission_level=channel.permission_level,
                    is_enabled=channel.is_enabled,
                    is_created=channel.is_created,
                    nsfw=channel.nsfw,
                    slowmode_delay=channel.slowmode_delay,
                    topic=channel.topic,
                    thread_config=channel.thread_config.to_dict() if channel.thread_config else None,
                    metadata_json=channel.metadata or {}  # Changed from metadata to metadata_json
                )
                
                session.add(entity)
                await session.flush()
                
                # Create the permissions
                for permission in channel.permissions:
                    perm_entity = ChannelPermissionEntity(
                        channel_id=entity.id,
                        role_id=permission.role_id,
                        view=permission.view,
                        send_messages=permission.send_messages,
                        read_messages=permission.read_messages,
                        manage_messages=permission.manage_messages,
                        manage_channel=permission.manage_channel,
                        use_bots=permission.use_bots,
                        embed_links=permission.embed_links,
                        attach_files=permission.attach_files,
                        add_reactions=permission.add_reactions
                    )
                    session.add(perm_entity)
                
                await session.commit()
                
                return self._entity_to_model(entity)
        finally:
            if session != self.session_or_service:
                await session.close() 