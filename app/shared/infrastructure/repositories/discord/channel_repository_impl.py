from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.shared.domain.models.discord.channel_model import (
    ChannelModel, ChannelTemplate, ChannelPermission, ThreadConfig
)
from app.shared.domain.repositories.discord.channel_repository import ChannelRepository
from app.shared.infrastructure.models.discord.channel_entity import ChannelEntity, ChannelPermissionEntity
from app.shared.infrastructure.database.api import get_session
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
            # Assume it's a database service or we need to get a new session
            return await get_session()
    
    def _entity_to_model(self, entity: ChannelEntity) -> ChannelModel:
        """Convert a database entity to a domain model"""
        permissions = []
        for perm_entity in entity.permissions:
            permissions.append(
                ChannelPermission(
                    role_id=perm_entity.role_id,
                    view=perm_entity.view,
                    send_messages=perm_entity.send_messages,
                    read_messages=perm_entity.read_messages,
                    manage_messages=perm_entity.manage_messages,
                    manage_channel=perm_entity.manage_channel,
                    use_bots=perm_entity.use_bots,
                    embed_links=perm_entity.embed_links,
                    attach_files=perm_entity.attach_files,
                    add_reactions=perm_entity.add_reactions
                )
            )
        
        # Convert thread_config from JSON to ThreadConfig object
        thread_config = None
        if entity.thread_config:
            thread_config = ThreadConfig(
                default_auto_archive_duration=entity.thread_config.get('default_auto_archive_duration', 1440),
                default_thread_slowmode_delay=entity.thread_config.get('default_thread_slowmode_delay', 0),
                default_reaction_emoji=entity.thread_config.get('default_reaction_emoji'),
                require_tag=entity.thread_config.get('require_tag', False),
                available_tags=entity.thread_config.get('available_tags', [])
            )
        
        return ChannelModel(
            id=entity.id,
            discord_id=entity.discord_id,
            name=entity.name,
            description=entity.description,
            category_id=entity.category_id,
            category_discord_id=entity.category_discord_id,
            type=entity.type,
            position=entity.position,
            permission_level=entity.permission_level,
            permissions=permissions,
            is_enabled=entity.is_enabled,
            is_created=entity.is_created,
            nsfw=entity.nsfw,
            slowmode_delay=entity.slowmode_delay,
            topic=entity.topic,
            thread_config=thread_config,
            metadata=entity.metadata_json or {}  # Use metadata_json here
        )
    
    def _model_to_entity(self, model: ChannelModel) -> ChannelEntity:
        """Convert domain model to database entity"""
        thread_config_dict = None
        if model.thread_config:
            thread_config_dict = {
                'default_auto_archive_duration': model.thread_config.default_auto_archive_duration,
                'default_thread_slowmode_delay': model.thread_config.default_thread_slowmode_delay,
                'default_reaction_emoji': model.thread_config.default_reaction_emoji,
                'require_tag': model.thread_config.require_tag,
                'available_tags': model.thread_config.available_tags
            }
        
        entity = ChannelEntity(
            name=model.name,
            discord_id=model.discord_id,
            description=model.description,
            category_id=model.category_id,
            category_discord_id=model.category_discord_id,
            type=model.type,
            position=model.position,
            permission_level=model.permission_level,
            is_enabled=model.is_enabled,
            is_created=model.is_created,
            nsfw=model.nsfw,
            slowmode_delay=model.slowmode_delay,
            topic=model.topic,
            thread_config=thread_config_dict,
            metadata_json=model.metadata
        )
        
        if model.id:
            entity.id = model.id
            
        entity.permissions = [
            ChannelPermissionEntity(
                role_id=perm.role_id,
                view=perm.view,
                send_messages=perm.send_messages,
                read_messages=perm.read_messages,
                manage_messages=perm.manage_messages,
                manage_channel=perm.manage_channel,
                use_bots=perm.use_bots,
                embed_links=perm.embed_links,
                attach_files=perm.attach_files,
                add_reactions=perm.add_reactions
            )
            for perm in model.permissions
        ]
        
        return entity
    
    async def get_all_channels(self) -> List[ChannelModel]:
        """Get all channels from the database"""
        session = await self._get_session()
        try:
            # Use selectinload to eagerly load permissions
            result = await session.execute(
                select(ChannelEntity).options(selectinload(ChannelEntity.permissions))
            )
            channels = result.scalars().all()
            return [self._entity_to_model(channel) for channel in channels]
        finally:
            # Only close if we created a new session
            if session != self.session_or_service:
                await session.close()
    
    async def get_channel_by_id(self, channel_id: int) -> Optional[ChannelModel]:
        """Get a channel by its database ID"""
        session = await self._get_session()
        try:
            channel = await session.get(ChannelEntity, channel_id)
            return self._entity_to_model(channel) if channel else None
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def get_channel_by_discord_id(self, discord_id: int) -> Optional[ChannelModel]:
        """Get a channel by its Discord ID"""
        session = await self._get_session()
        try:
            channel = await session.get(ChannelEntity, {'discord_id': discord_id})
            return self._entity_to_model(channel) if channel else None
        finally:
            if session != self.session_or_service:
                await session.close()
    
    async def get_channel_by_name_and_category(self, name: str, category_id: int) -> Optional[ChannelModel]:
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
    
    async def get_channels_by_category_id(self, category_id: int) -> List[ChannelModel]:
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
    
    async def get_channels_by_category_discord_id(self, category_discord_id: int) -> List[ChannelModel]:
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
    
    async def save_channel(self, channel: ChannelModel) -> ChannelModel:
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
    
    async def create_from_template(self, template: ChannelTemplate, category_id: int) -> ChannelModel:
        """Create a new channel from a template"""
        session = await self._get_session()
        close_session = session != self.session_or_service
        
        try:
            # Convert template to model
            model = template.to_channel_model(category_id)
            
            # Convert model to entity
            entity = self._model_to_entity(model)
            
            # Check if we need to manage the transaction or not
            if session.in_transaction():
                # A transaction is already active, just add the entity
                session.add(entity)
                await session.flush()
            else:
                # No active transaction, start one
                async with session.begin():
                    session.add(entity)
                    await session.flush()
            
            # Update the ID
            model.id = entity.id
            
            return model
        except Exception as e:
            logger.error(f"Error creating channel from template: {e}")
            raise
        finally:
            if close_session:
                await session.close()
    
    async def get_enabled_channels(self) -> List[ChannelModel]:
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
    
    async def get_channels_by_type(self, channel_type: str) -> List[ChannelModel]:
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
    
    async def get_channel_mapping(self) -> Dict[str, ChannelModel]:
        """Get a mapping of channel names to channel models"""
        session = await self._get_session()
        try:
            channels = await self.get_all_channels()
            return {channel.name: channel for channel in channels}
        finally:
            if session != self.session_or_service:
                await session.close()

    async def create_channel(self, channel: ChannelModel) -> ChannelModel:
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