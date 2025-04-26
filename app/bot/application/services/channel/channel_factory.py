import nextcord
import logging
from typing import Optional, Dict, Any, List
from app.shared.infrastructure.models.discord.entities.channel_entity import ChannelEntity, ChannelPermissionEntity
from app.shared.infrastructure.models.discord.enums.channels import ChannelType, ChannelPermissionLevel
from app.shared.domain.repositories.discord.channel_repository import ChannelRepository
from app.shared.domain.repositories.discord.category_repository import CategoryRepository
from app.bot.application.services.channel.channel_builder import ChannelBuilder

logger = logging.getLogger(__name__)

class ChannelFactory:
    """Factory for creating specialized channels with predefined configurations"""
    
    def __init__(self, channel_repository: ChannelRepository, 
                 category_repository: CategoryRepository,
                 channel_builder: ChannelBuilder):
        self.channel_repository = channel_repository
        self.category_repository = category_repository
        self.channel_builder = channel_builder
    
    async def create_game_server_channel(
        self, 
        guild: nextcord.Guild, 
        game_name: str,
        category_name: str = "GAME SERVERS",
        permissions: List[ChannelPermissionEntity] = None,
        metadata_json: Dict[str, Any] = None
    ) -> Optional[discord.TextChannel]:
        """Create a channel for a specific game server"""
        
        if permissions is None:
            permissions = []
            
        if metadata_json is None:
            metadata_json = {}
            
        metadata_json["game_type"] = game_name.lower()
        metadata_json["icon"] = self._get_game_icon(game_name)
        
        # Find category
        category = self.category_repository.get_category_by_name(category_name)
        if not category:
            logger.error(f"Category not found: {category_name}")
            return None
        
        # Get the last position in the category
        existing_channels = self.channel_repository.get_channels_by_category_id(category.id)
        position = 0
        if existing_channels:
            position = max(ch.position for ch in existing_channels) + 1
        
        # Create a game server channel model
        channel = ChannelEntity(
            name=game_name.lower(),
            description=f"{game_name} server channel",
            category_id=category.id,
            category_discord_id=category.discord_id,
            type=ChannelType.TEXT,
            position=position,
            permission_level=ChannelPermissionLevel.MEMBER,
            permissions=permissions,
            topic=f"{game_name} server discussion and status updates",
            metadata_json=metadata_json
        )
        
        # First check if this is an update or a new channel
        existing = self.channel_repository.get_channel_by_name_and_category(
            channel.name, 
            channel.category_id
        )
        if existing:
            # Update existing channel
            channel.id = existing.id
        saved_channel = self.channel_repository.save_channel(channel)
        
        # Create in Discord
        discord_channel = await self.channel_builder.create_channel(guild, saved_channel)
        return discord_channel
    
    async def create_project_channel(
        self, 
        guild: nextcord.Guild, 
        project_name: str,
        description: str = None,
        category_name: str = "PROJECTS",
        permissions: List[ChannelPermissionEntity] = None,
        metadata_json: Dict[str, Any] = None
    ) -> Optional[discord.TextChannel]:
        """Create a channel for a specific project"""
        
        if permissions is None:
            permissions = []
            
        if metadata_json is None:
            metadata_json = {}
            
        metadata_json["project_name"] = project_name
        metadata_json["icon"] = "🛠️"
        
        # Find category
        category = self.category_repository.get_category_by_name(category_name)
        if not category:
            logger.error(f"Category not found: {category_name}")
            return None
        
        # Get the last position in the category
        existing_channels = self.channel_repository.get_channels_by_category_id(category.id)
        position = 0
        if existing_channels:
            position = max(ch.position for ch in existing_channels) + 1
        
        # Create a project channel model
        channel = ChannelEntity(
            name=f"project-{project_name.lower().replace(' ', '-')}",
            description=description or f"Discussion for {project_name} project",
            category_id=category.id,
            category_discord_id=category.discord_id,
            type=ChannelType.TEXT,
            position=position,
            permission_level=ChannelPermissionLevel.MEMBER,
            permissions=permissions,
            topic=description or f"Discussion for {project_name} project",
            metadata_json=metadata_json
        )
        
        # First check if this is an update or a new channel
        existing = self.channel_repository.get_channel_by_name_and_category(
            channel.name, 
            channel.category_id
        )
        if existing:
            # Update existing channel
            channel.id = existing.id
        saved_channel = self.channel_repository.save_channel(channel)
        
        # Create in Discord
        discord_channel = await self.channel_builder.create_channel(guild, saved_channel)
        return discord_channel
    
    async def create_forum_channel(
        self, 
        guild: nextcord.Guild, 
        name: str,
        description: str,
        category_name: str,
        available_tags: List[Dict[str, Any]] = None,
        require_tag: bool = True,
        permissions: List[ChannelPermissionEntity] = None,
        metadata_json: Dict[str, Any] = None
    ) -> Optional[discord.ForumChannel]:
        """Create a forum channel with tags"""
        
        if permissions is None:
            permissions = []
            
        if metadata_json is None:
            metadata_json = {}
            
        if available_tags is None:
            available_tags = [
                {"name": "Discussion", "emoji": "💬"},
                {"name": "Question", "emoji": "❓"},
                {"name": "Announcement", "emoji": "📢"}
            ]
            
        # Find category
        category = self.category_repository.get_category_by_name(category_name)
        if not category:
            logger.error(f"Category not found: {category_name}")
            return None
        
        # Get the last position in the category
        existing_channels = self.channel_repository.get_channels_by_category_id(category.id)
        position = 0
        if existing_channels:
            position = max(ch.position for ch in existing_channels) + 1
        
        # Create thread config
        thread_config = {
            "default_auto_archive_duration": 10080,  # 7 days
            "default_thread_slowmode_delay": 0,
            "require_tag": require_tag,
            "available_tags": available_tags
        }
        
        # Create a forum channel model
        channel = ChannelEntity(
            name=name.lower().replace(' ', '-'),
            description=description,
            category_id=category.id,
            category_discord_id=category.discord_id,
            type=ChannelType.FORUM,
            position=position,
            permission_level=ChannelPermissionLevel.MEMBER,
            permissions=permissions,
            topic=description,
            thread_config=thread_config,
            metadata_json=metadata_json
        )
        
        # First check if this is an update or a new channel
        existing = self.channel_repository.get_channel_by_name_and_category(
            channel.name, 
            channel.category_id
        )
        if existing:
            # Update existing channel
            channel.id = existing.id
        saved_channel = self.channel_repository.save_channel(channel)
        
        # Create in Discord
        discord_channel = await self.channel_builder.create_channel(guild, saved_channel)
        return discord_channel
    
    def _get_game_icon(self, game_name: str) -> str:
        """Get an appropriate icon for a game server"""
        game_icons = {
            "minecraft": "⛏️",
            "valheim": "🪓",
            "terraria": "🌎",
            "ark": "🦖",
            "factorio": "🏭",
            "rust": "🔫",
            "csgo": "💣",
            "teamfortress": "🎮",
            "satisfactory": "🏗️",
            "amongus": "👨‍🚀"
        }
        
        game_name_lower = game_name.lower()
        for key, icon in game_icons.items():
            if key in game_name_lower:
                return icon
        
        return "🎮"  # Default game icon 