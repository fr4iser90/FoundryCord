from typing import Optional, List, Dict, Any
import nextcord
import logging
from app.shared.infrastructure.models.discord.entities.channel_entity import ChannelEntity
from app.shared.infrastructure.models.discord.enums.channels import ChannelType
from app.shared.domain.repositories.discord.channel_repository import ChannelRepository
from app.shared.domain.repositories.discord.category_repository import CategoryRepository
from app.shared.infrastructure.repositories.discord.channel_repository_impl import ChannelRepositoryImpl
from app.shared.infrastructure.repositories.discord.category_repository_impl import CategoryRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.database.session.context import session_context

logger = logging.getLogger(__name__)

class ChannelBuilder:
    """Service for building Discord channels from database models"""
    
    def __init__(self):
        pass
    
    async def create_channel(self, guild: nextcord.Guild, channel: ChannelEntity, session: AsyncSession) -> Optional[nextcord.abc.GuildChannel]:
        """Create a Discord channel from a channel model"""
        if not channel.is_valid:
            logger.warning(f"Invalid channel configuration: {channel.name}")
            return None
        
        category_repo = CategoryRepositoryImpl(session)
        channel_repo = ChannelRepositoryImpl(session)

        # Get the category
        category = None
        if channel.category_discord_id:
            category = nextcord.utils.get(guild.categories, id=channel.category_discord_id)
        elif channel.category_id:
            db_category = await category_repo.get_by_id(channel.category_id)
            if db_category and db_category.discord_id:
                category = nextcord.utils.get(guild.categories, id=db_category.discord_id)
        
        if not category and (channel.category_id or channel.category_discord_id):
            logger.warning(f"Category not found for channel: {channel.name}")
            return None
        
        # Create channel overwrites for permissions
        overwrites = {}
        await session.refresh(channel, ['permissions'])
        if hasattr(channel, 'permissions') and channel.permissions:
            for permission in channel.permissions:
                role = guild.get_role(permission.role_id)
                if role:
                    overwrite = nextcord.PermissionOverwrite()
                    overwrite.view_channel = getattr(permission, 'view_channel', None)
                    overwrite.send_messages = getattr(permission, 'send_messages', None)
                    overwrite.read_messages = getattr(permission, 'read_messages', None)
                    overwrite.manage_messages = getattr(permission, 'manage_messages', None)
                    overwrite.manage_channels = getattr(permission, 'manage_channel', None)
                    # Additional permissions
                    overwrite.embed_links = getattr(permission, 'embed_links', None)
                    overwrite.attach_files = getattr(permission, 'attach_files', None)
                    overwrite.add_reactions = getattr(permission, 'add_reactions', None)
                    overwrites[role] = overwrite
        
        try:
            discord_channel = None
            
            # Create the channel based on its type
            creation_kwargs = {
                 'name': channel.name,
                 'overwrites': overwrites,
                 'category': category,
                 'position': channel.position,
                 'reason': "Channel setup from database"
            }

            if channel.type == ChannelType.TEXT:
                creation_kwargs.update({
                    'topic': channel.topic,
                    'slowmode_delay': channel.slowmode_delay,
                    'nsfw': channel.nsfw
                })
                discord_channel = await guild.create_text_channel(**creation_kwargs)
                
            elif channel.type == ChannelType.VOICE:
                discord_channel = await guild.create_voice_channel(**creation_kwargs)
                
            elif channel.type == ChannelType.FORUM:
                # For forum channels, we need to handle tags and other forum-specific settings
                forum_tags = []
                if channel.thread_config and channel.thread_config.available_tags:
                    for tag_data in channel.thread_config.available_tags:
                        forum_tags.append(nextcord.ForumTag(
                            name=tag_data.get('name', 'Tag'),
                            emoji=tag_data.get('emoji'),
                            moderated=tag_data.get('moderated', False)
                        ))
                
                default_reaction = None
                if channel.thread_config and channel.thread_config.default_reaction_emoji:
                    default_reaction = channel.thread_config.default_reaction_emoji
                
                discord_channel = await guild.create_forum(**creation_kwargs)
                
            elif channel.type == ChannelType.ANNOUNCEMENT:
                creation_kwargs['news'] = True  # This makes it an announcement channel
                discord_channel = await guild.create_text_channel(**creation_kwargs)
                
            elif channel.type == ChannelType.STAGE:
                discord_channel = await guild.create_stage_channel(**creation_kwargs)
            
            if discord_channel:
                # Update the channel in the database with the Discord ID
                await channel_repo.update_discord_id(channel.id, discord_channel.id)
                logger.info(f"Created channel: {channel.name} (ID: {discord_channel.id})")
                return discord_channel
            
        except nextcord.Forbidden:
            logger.error(f"Bot lacks permissions to create channel: {channel.name}")
            return None
        except nextcord.HTTPException as e:
            logger.error(f"Failed to create channel {channel.name}: {str(e)}")
            return None
    
    async def setup_all_channels(self, guild: nextcord.Guild, 
                              category_map: Dict[str, nextcord.CategoryChannel], 
                              session: AsyncSession) -> Dict[str, nextcord.abc.GuildChannel]:
        """Set up all enabled channels from the database"""
        channel_repo = ChannelRepositoryImpl(session)
        category_repo = CategoryRepositoryImpl(session)

        # channels = await channel_repo.get_enabled_channels()
        channels = await channel_repo.get_all_channels()
        enabled_channels = [ch for ch in channels if ch.is_enabled]

        created_channels = {}
        
        # Sort channels by position
        enabled_channels.sort(key=lambda c: c.position)
        
        # Associate channels with their categories by name if category_map is provided
        if category_map:
            for channel in enabled_channels:
                # Find the category for this channel if not already set
                if not channel.category_discord_id and channel.category_id:
                    category = await category_repo.get_by_id(channel.category_id)
                    if category and category.name in category_map:
                        discord_category = category_map[category.name]
                        channel.category_discord_id = discord_category.id
                        # Update in DB
                        await channel_repo.save_channel(channel)
        
        # Create channels in Discord
        for channel in enabled_channels:
            # Skip if channel is already created in Discord
            discord_channel_object = None
            if channel.discord_id:
                existing = nextcord.utils.get(guild.channels, id=channel.discord_id)
                if existing:
                    discord_channel_object = existing
                    # created_channels[channel.name] = existing # Map later after creation/update
                    # continue # Don't skip, might need updates
            
            if discord_channel_object:
                 # TODO: Add logic to update existing channel if needed (name, topic, permissions etc.)
                 created_channels[channel.name] = discord_channel_object # Add existing to map
            else:    
                # Create the channel
                discord_channel_object = await self.create_channel(guild, channel, session)
            
            if discord_channel_object:
                created_channels[channel.name] = discord_channel_object
        
        return created_channels
    
    async def sync_channels(self, guild: nextcord.Guild, session: AsyncSession) -> None:
        """Sync database channels with existing Discord channels"""
        temp_channel_repo = ChannelRepositoryImpl(session)
        temp_category_repo = CategoryRepositoryImpl(session)
            
        for discord_channel in guild.channels:
            # Skip categories
            if isinstance(discord_channel, nextcord.CategoryChannel):
                continue
                
            # Check if channel exists in database by discord_id
            channel = await temp_channel_repo.get_channel_by_discord_id(discord_channel.id)
            if not channel:
                # Try to find by name and category
                db_category = None
                if discord_channel.category:
                    db_category = await temp_category_repo.get_by_discord_id(discord_channel.category.id)
                
                if db_category: 
                    # Implement query directly:
                    chan_result = await session.execute(
                        select(ChannelEntity).where(
                            ChannelEntity.name == discord_channel.name, 
                            ChannelEntity.category_id == db_category.id
                        )
                    )
                    channel = chan_result.scalars().first()
                
                if channel:
                    # Update Discord ID
                    await temp_channel_repo.update_discord_id(channel.id, discord_channel.id)
                    logger.info(f"Linked existing channel: {discord_channel.name} (ID: {discord_channel.id})")
        
        logger.info("Channel synchronization completed") 