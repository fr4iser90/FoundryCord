from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.bot.domain.channels.models.channel_model import (
    ChannelModel, ChannelTemplate, ChannelPermission, ThreadConfig
)
from app.bot.domain.channels.repositories.channel_repository import ChannelRepository
from app.bot.infrastructure.database.models.channel_entity import ChannelEntity, ChannelPermissionEntity
from app.shared.infrastructure.database.service import DatabaseService
import logging

logger = logging.getLogger(__name__)


class ChannelRepositoryImpl(ChannelRepository):
    """Implementation of the Channel repository"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
    
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
    
    def get_all_channels(self) -> List[ChannelModel]:
        """Get all channels from the database"""
        with self.db_service.session() as session:
            channels = session.query(ChannelEntity).all()
            return [self._entity_to_model(channel) for channel in channels]
    
    def get_channel_by_id(self, channel_id: int) -> Optional[ChannelModel]:
        """Get a channel by its database ID"""
        with self.db_service.session() as session:
            channel = session.query(ChannelEntity).filter(ChannelEntity.id == channel_id).first()
            return self._entity_to_model(channel) if channel else None
    
    def get_channel_by_discord_id(self, discord_id: int) -> Optional[ChannelModel]:
        """Get a channel by its Discord ID"""
        with self.db_service.session() as session:
            channel = session.query(ChannelEntity).filter(ChannelEntity.discord_id == discord_id).first()
            return self._entity_to_model(channel) if channel else None
    
    def get_channel_by_name_and_category(self, name: str, category_id: int) -> Optional[ChannelModel]:
        """Get a channel by its name and category ID"""
        with self.db_service.session() as session:
            channel = session.query(ChannelEntity).filter(
                ChannelEntity.name == name,
                ChannelEntity.category_id == category_id
            ).first()
            return self._entity_to_model(channel) if channel else None
    
    def get_channels_by_category_id(self, category_id: int) -> List[ChannelModel]:
        """Get all channels in a specific category"""
        with self.db_service.session() as session:
            channels = session.query(ChannelEntity).filter(
                ChannelEntity.category_id == category_id
            ).all()
            return [self._entity_to_model(channel) for channel in channels]
    
    def get_channels_by_category_discord_id(self, category_discord_id: int) -> List[ChannelModel]:
        """Get all channels in a specific Discord category"""
        with self.db_service.session() as session:
            channels = session.query(ChannelEntity).filter(
                ChannelEntity.category_discord_id == category_discord_id
            ).all()
            return [self._entity_to_model(channel) for channel in channels]
    
    def save_channel(self, channel: ChannelModel) -> ChannelModel:
        """Save a channel to the database (create or update)"""
        with self.db_service.session() as session:
            # Convert ThreadConfig to dict for JSON serialization
            thread_config_dict = None
            if channel.thread_config:
                thread_config_dict = {
                    'default_auto_archive_duration': channel.thread_config.default_auto_archive_duration,
                    'default_thread_slowmode_delay': channel.thread_config.default_thread_slowmode_delay,
                    'default_reaction_emoji': channel.thread_config.default_reaction_emoji,
                    'require_tag': channel.thread_config.require_tag,
                    'available_tags': channel.thread_config.available_tags or []
                }
            
            # Check if this is an update (existing ID)
            if channel.id:
                existing = session.query(ChannelEntity).filter(ChannelEntity.id == channel.id).first()
                if existing:
                    # Update existing entity
                    existing.name = channel.name
                    existing.description = channel.description
                    existing.category_id = channel.category_id
                    existing.category_discord_id = channel.category_discord_id
                    existing.type = channel.type
                    existing.position = channel.position
                    existing.permission_level = channel.permission_level
                    existing.is_enabled = channel.is_enabled
                    existing.is_created = channel.is_created
                    existing.nsfw = channel.nsfw
                    existing.slowmode_delay = channel.slowmode_delay
                    existing.topic = channel.topic
                    existing.thread_config = thread_config_dict  # Use the dict instead of the object
                    existing.metadata_json = channel.metadata
                    
                    # Update permissions
                    # First, remove all existing permissions
                    for perm in existing.permissions:
                        session.delete(perm)
                    
                    # Then add the new permissions
                    for perm in channel.permissions:
                        perm_entity = ChannelPermissionEntity(
                            channel_id=existing.id,
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
                        session.add(perm_entity)
                    
                    session.commit()
                    return self._entity_to_model(existing)
            
            # If we get here, we need to create a new channel
            # But first, check if a channel with the same name and category already exists
            existing_by_name = None
            if channel.category_id:
                existing_by_name = session.query(ChannelEntity).filter(
                    ChannelEntity.name == channel.name,
                    ChannelEntity.category_id == channel.category_id
                ).first()
            
            if existing_by_name:
                # Update the existing channel instead of creating a new one
                existing_by_name.description = channel.description
                existing_by_name.category_discord_id = channel.category_discord_id
                existing_by_name.type = channel.type
                existing_by_name.position = channel.position
                existing_by_name.permission_level = channel.permission_level
                existing_by_name.is_enabled = channel.is_enabled
                existing_by_name.is_created = channel.is_created
                existing_by_name.nsfw = channel.nsfw
                existing_by_name.slowmode_delay = channel.slowmode_delay
                existing_by_name.topic = channel.topic
                existing_by_name.thread_config = thread_config_dict  # Use the dict instead of the object
                existing_by_name.metadata_json = channel.metadata
                
                # Update permissions
                # First, remove all existing permissions
                for perm in existing_by_name.permissions:
                    session.delete(perm)
                
                # Then add the new permissions
                for perm in channel.permissions:
                    perm_entity = ChannelPermissionEntity(
                        channel_id=existing_by_name.id,
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
                    session.add(perm_entity)
                
                session.commit()
                return self._entity_to_model(existing_by_name)
            
            # Create a new entity
            entity = ChannelEntity(
                name=channel.name,
                description=channel.description,
                category_id=channel.category_id,
                category_discord_id=channel.category_discord_id,
                discord_id=channel.discord_id,
                type=channel.type,
                position=channel.position,
                permission_level=channel.permission_level,
                is_enabled=channel.is_enabled,
                is_created=channel.is_created,
                nsfw=channel.nsfw,
                slowmode_delay=channel.slowmode_delay,
                topic=channel.topic,
                thread_config=thread_config_dict,  # Use the dict instead of the object
                metadata_json=channel.metadata
            )
            
            # Don't set the ID manually - let the database assign it
            # This prevents duplicate key errors
            if channel.id:
                # Only set the ID if we're sure it doesn't exist
                check = session.query(ChannelEntity).filter(ChannelEntity.id == channel.id).first()
                if not check:
                    entity.id = channel.id
            
            session.add(entity)
            session.flush()  # This assigns an ID if we didn't set one
            
            # Add permissions
            for perm in channel.permissions:
                perm_entity = ChannelPermissionEntity(
                    channel_id=entity.id,
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
                session.add(perm_entity)
            
            try:
                session.commit()
            except Exception as e:
                logger.error(f"Error saving channel: {e}")
                session.rollback()
                raise
            
            return self._entity_to_model(entity)
    
    def update_discord_id(self, channel_id: int, discord_id: int) -> bool:
        """Update the Discord ID of a channel after it's created in Discord"""
        with self.db_service.session() as session:
            channel = session.query(ChannelEntity).filter(ChannelEntity.id == channel_id).first()
            if channel:
                channel.discord_id = discord_id
                channel.is_created = True
                session.commit()
                return True
            return False
    
    def update_channel_status(self, channel_id: int, is_created: bool) -> bool:
        """Update the creation status of a channel"""
        with self.db_service.session() as session:
            channel = session.query(ChannelEntity).filter(ChannelEntity.id == channel_id).first()
            if channel:
                channel.is_created = is_created
                session.commit()
                return True
            return False
    
    def delete_channel(self, channel_id: int) -> bool:
        """Delete a channel from the database"""
        with self.db_service.session() as session:
            channel = session.query(ChannelEntity).filter(ChannelEntity.id == channel_id).first()
            if channel:
                session.delete(channel)
                session.commit()
                return True
            return False
    
    def create_from_template(self, template: ChannelTemplate, category_id: Optional[int] = None, 
                           category_discord_id: Optional[int] = None) -> ChannelModel:
        """Create a new channel from a template"""
        model = template.to_channel_model(category_id, category_discord_id)
        return self.save_channel(model)
    
    def get_enabled_channels(self) -> List[ChannelModel]:
        """Get all enabled channels"""
        with self.db_service.session() as session:
            channels = session.query(ChannelEntity).filter(ChannelEntity.is_enabled == True).all()
            return [self._entity_to_model(channel) for channel in channels]
    
    def get_channels_by_type(self, channel_type: str) -> List[ChannelModel]:
        """Get all channels of a specific type"""
        with self.db_service.session() as session:
            channels = session.query(ChannelEntity).filter(ChannelEntity.type == channel_type).all()
            return [self._entity_to_model(channel) for channel in channels]
    
    def get_channel_mapping(self) -> Dict[str, ChannelModel]:
        """Get a mapping of channel names to channel models"""
        channels = self.get_all_channels()
        return {channel.name: channel for channel in channels}

    def create_channel(self, channel: ChannelModel) -> ChannelModel:
        """Create a new channel"""
        with self.db_service.session() as session:
            # Create the channel entity
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
            session.flush()
            
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
            
            session.commit()
            
            return self._entity_to_model(entity) 