from typing import Optional, List, Dict, Any
import discord
import logging
from app.bot.domain.channels.models.channel_model import ChannelModel, ChannelType
from app.bot.domain.channels.repositories.channel_repository import ChannelRepository
from app.bot.domain.categories.repositories.category_repository import CategoryRepository

logger = logging.getLogger(__name__)

class ChannelBuilder:
    """Service for building Discord channels from database models"""
    
    def __init__(self, channel_repository: ChannelRepository, category_repository: CategoryRepository):
        self.channel_repository = channel_repository
        self.category_repository = category_repository
    
    async def create_channel(self, guild: discord.Guild, channel: ChannelModel) -> Optional[discord.abc.GuildChannel]:
        """Create a Discord channel from a channel model"""
        if not channel.is_valid:
            logger.warning(f"Invalid channel configuration: {channel.name}")
            return None
        
        # Get the category
        category = None
        if channel.category_discord_id:
            category = discord.utils.get(guild.categories, id=channel.category_discord_id)
        elif channel.category_id:
            db_category = self.category_repository.get_category_by_id(channel.category_id)
            if db_category and db_category.discord_id:
                category = discord.utils.get(guild.categories, id=db_category.discord_id)
        
        if not category and (channel.category_id or channel.category_discord_id):
            logger.warning(f"Category not found for channel: {channel.name}")
            return None
        
        # Create channel overwrites for permissions
        overwrites = {}
        for permission in channel.permissions:
            role = guild.get_role(permission.role_id)
            if role:
                overwrite = discord.PermissionOverwrite()
                overwrite.view_channel = permission.view
                overwrite.send_messages = permission.send_messages
                overwrite.read_messages = permission.read_messages
                overwrite.manage_messages = permission.manage_messages
                overwrite.manage_channels = permission.manage_channel
                # Additional permissions
                overwrite.embed_links = permission.embed_links
                overwrite.attach_files = permission.attach_files
                overwrite.add_reactions = permission.add_reactions
                overwrites[role] = overwrite
        
        try:
            discord_channel = None
            
            # Create the channel based on its type
            if channel.type == ChannelType.TEXT:
                discord_channel = await guild.create_text_channel(
                    name=channel.name,
                    overwrites=overwrites,
                    category=category,
                    topic=channel.topic,
                    slowmode_delay=channel.slowmode_delay,
                    nsfw=channel.nsfw,
                    position=channel.position,
                    reason="Channel setup from database"
                )
                
            elif channel.type == ChannelType.VOICE:
                discord_channel = await guild.create_voice_channel(
                    name=channel.name,
                    overwrites=overwrites,
                    category=category,
                    position=channel.position,
                    reason="Channel setup from database"
                )
                
            elif channel.type == ChannelType.FORUM:
                # For forum channels, we need to handle tags and other forum-specific settings
                forum_tags = []
                if channel.thread_config and channel.thread_config.available_tags:
                    for tag_data in channel.thread_config.available_tags:
                        forum_tags.append(discord.ForumTag(
                            name=tag_data.get('name', 'Tag'),
                            emoji=tag_data.get('emoji'),
                            moderated=tag_data.get('moderated', False)
                        ))
                
                default_reaction = None
                if channel.thread_config and channel.thread_config.default_reaction_emoji:
                    default_reaction = channel.thread_config.default_reaction_emoji
                
                discord_channel = await guild.create_forum(
                    name=channel.name,
                    overwrites=overwrites,
                    category=category,
                    topic=channel.topic,
                    slowmode_delay=channel.slowmode_delay,
                    nsfw=channel.nsfw,
                    position=channel.position,
                    reason="Channel setup from database",
                    available_tags=forum_tags,
                    default_auto_archive_duration=channel.thread_config.default_auto_archive_duration if channel.thread_config else 1440,
                    default_reaction_emoji=default_reaction,
                    default_thread_slowmode_delay=channel.thread_config.default_thread_slowmode_delay if channel.thread_config else 0,
                    require_tag=channel.thread_config.require_tag if channel.thread_config else False
                )
                
            elif channel.type == ChannelType.ANNOUNCEMENT:
                discord_channel = await guild.create_text_channel(
                    name=channel.name,
                    overwrites=overwrites,
                    category=category,
                    topic=channel.topic,
                    slowmode_delay=channel.slowmode_delay,
                    nsfw=channel.nsfw,
                    position=channel.position,
                    reason="Channel setup from database",
                    news=True  # This makes it an announcement channel
                )
                
            elif channel.type == ChannelType.STAGE:
                discord_channel = await guild.create_stage_channel(
                    name=channel.name,
                    overwrites=overwrites,
                    category=category,
                    position=channel.position,
                    reason="Channel setup from database"
                )
            
            if discord_channel:
                # Update the channel in the database with the Discord ID
                self.channel_repository.update_discord_id(channel.id, discord_channel.id)
                logger.info(f"Created channel: {channel.name} (ID: {discord_channel.id})")
                return discord_channel
            
        except discord.Forbidden:
            logger.error(f"Bot lacks permissions to create channel: {channel.name}")
            return None
        except discord.HTTPException as e:
            logger.error(f"Failed to create channel {channel.name}: {str(e)}")
            return None
    
    async def setup_all_channels(self, guild: discord.Guild, 
                              category_map: Dict[str, discord.CategoryChannel] = None) -> Dict[str, discord.abc.GuildChannel]:
        """Set up all enabled channels from the database"""
        channels = self.channel_repository.get_enabled_channels()
        created_channels = {}
        
        # Sort channels by position
        channels.sort(key=lambda c: c.position)
        
        # Associate channels with their categories by name if category_map is provided
        if category_map:
            for channel in channels:
                # Find the category for this channel if not already set
                if not channel.category_discord_id:
                    category = self.category_repository.get_category_by_id(channel.category_id)
                    if category and category.name in category_map:
                        discord_category = category_map[category.name]
                        channel.category_discord_id = discord_category.id
                        # Update in DB
                        self.channel_repository.save_channel(channel)
        
        # Create channels in Discord
        for channel in channels:
            # Skip if channel is already created in Discord
            if channel.discord_id:
                existing = discord.utils.get(guild.channels, id=channel.discord_id)
                if existing:
                    created_channels[channel.name] = existing
                    continue
                
                # Create the channel
                discord_channel = await self.create_channel(guild, channel)
                if discord_channel:
                    created_channels[channel.name] = discord_channel
        
        return created_channels
    
    async def sync_channels(self, guild: discord.Guild) -> None:
        """Sync database channels with existing Discord channels"""
        for discord_channel in guild.channels:
            # Skip categories
            if isinstance(discord_channel, discord.CategoryChannel):
                continue
                
            # Check if channel exists in database
            channel = self.channel_repository.get_channel_by_discord_id(discord_channel.id)
            if not channel:
                # Try to find by name and category
                if discord_channel.category:
                    db_category = self.category_repository.get_category_by_discord_id(discord_channel.category.id)
                    if db_category:
                        channel = self.channel_repository.get_channel_by_name_and_category(
                            discord_channel.name, db_category.id
                        )
                
                if channel:
                    # Update Discord ID
                    self.channel_repository.update_discord_id(channel.id, discord_channel.id)
                    logger.info(f"Linked existing channel: {discord_channel.name} (ID: {discord_channel.id})") 