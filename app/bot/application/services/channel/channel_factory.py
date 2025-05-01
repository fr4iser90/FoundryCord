import nextcord
import logging
from typing import Optional, Dict, Any, List
from app.shared.infrastructure.models.discord.entities.channel_entity import ChannelEntity, ChannelPermissionEntity
from app.shared.infrastructure.models.discord.enums.channels import ChannelType, ChannelPermissionLevel
from app.shared.domain.repositories.discord.channel_repository import ChannelRepository
from app.shared.domain.repositories.discord.category_repository import CategoryRepository
from app.bot.application.services.channel.channel_builder import ChannelBuilder
from app.shared.infrastructure.repositories.discord.channel_repository_impl import ChannelRepositoryImpl
from app.shared.infrastructure.repositories.discord.category_repository_impl import CategoryRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

class ChannelFactory:
    """Factory for creating specialized channels with predefined configurations"""
    
    def __init__(self):
        pass
    
    async def create_game_server_channel(
        self, 
        guild: nextcord.Guild, 
        game_name: str,
        session: AsyncSession,
        category_name: str = "GAME SERVERS",
        permissions: List[ChannelPermissionEntity] = None,
        metadata_json: Dict[str, Any] = None
    ) -> Optional[nextcord.TextChannel]:
        """Create a channel for a specific game server"""
        
        channel_repo = ChannelRepositoryImpl(session)
        category_repo = CategoryRepositoryImpl(session)
        channel_builder = ChannelBuilder()
        
        if permissions is None:
            permissions = []
            
        if metadata_json is None:
            metadata_json = {}
            
        metadata_json["game_type"] = game_name.lower()
        metadata_json["icon"] = self._get_game_icon(game_name)
        
        cat_result = await session.execute(select(CategoryEntity).where(CategoryEntity.name == category_name))
        category = cat_result.scalars().first()
        if not category:
            logger.error(f"Category not found: {category_name}")
            return None
        
        chan_result = await session.execute(select(ChannelEntity).where(ChannelEntity.category_id == category.id))
        existing_channels = chan_result.scalars().all()
        position = 0
        if existing_channels:
            position = max(ch.position for ch in existing_channels) + 1
        
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
        
        exist_result = await session.execute(select(ChannelEntity).where(ChannelEntity.name == channel.name, ChannelEntity.category_id == channel.category_id))
        existing = exist_result.scalars().first()
        if existing:
            channel.id = existing.id
        saved_channel = await channel_repo.save_channel(channel)
        
        discord_channel = await channel_builder.create_channel(guild, saved_channel, session)
        return discord_channel
    
    async def create_project_channel(
        self, 
        guild: nextcord.Guild, 
        project_name: str,
        session: AsyncSession,
        description: str = None,
        category_name: str = "PROJECTS",
        permissions: List[ChannelPermissionEntity] = None,
        metadata_json: Dict[str, Any] = None
    ) -> Optional[nextcord.TextChannel]:
        """Create a channel for a specific project"""
        
        channel_repo = ChannelRepositoryImpl(session)
        category_repo = CategoryRepositoryImpl(session)
        channel_builder = ChannelBuilder()
        
        if permissions is None:
            permissions = []
            
        if metadata_json is None:
            metadata_json = {}
            
        metadata_json["project_name"] = project_name
        metadata_json["icon"] = "🛠️"
        
        cat_result = await session.execute(select(CategoryEntity).where(CategoryEntity.name == category_name))
        category = cat_result.scalars().first()
        if not category:
            logger.error(f"Category not found: {category_name}")
            return None
        
        chan_result = await session.execute(select(ChannelEntity).where(ChannelEntity.category_id == category.id))
        existing_channels = chan_result.scalars().all()
        position = 0
        if existing_channels:
            position = max(ch.position for ch in existing_channels) + 1
        
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
        
        exist_result = await session.execute(select(ChannelEntity).where(ChannelEntity.name == channel.name, ChannelEntity.category_id == channel.category_id))
        existing = exist_result.scalars().first()
        if existing:
            channel.id = existing.id
        saved_channel = await channel_repo.save_channel(channel)
        
        discord_channel = await channel_builder.create_channel(guild, saved_channel, session)
        return discord_channel
    
    async def create_forum_channel(
        self, 
        guild: nextcord.Guild, 
        name: str,
        description: str,
        category_name: str,
        session: AsyncSession,
        available_tags: List[Dict[str, Any]] = None,
        require_tag: bool = True,
        permissions: List[ChannelPermissionEntity] = None,
        metadata_json: Dict[str, Any] = None
    ) -> Optional[nextcord.ForumChannel]:
        """Create a forum channel with tags"""
        
        channel_repo = ChannelRepositoryImpl(session)
        category_repo = CategoryRepositoryImpl(session)
        channel_builder = ChannelBuilder()
        
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
            
        cat_result = await session.execute(select(CategoryEntity).where(CategoryEntity.name == category_name))
        category = cat_result.scalars().first()
        if not category:
            logger.error(f"Category not found: {category_name}")
            return None
        
        chan_result = await session.execute(select(ChannelEntity).where(ChannelEntity.category_id == category.id))
        existing_channels = chan_result.scalars().all()
        position = 0
        if existing_channels:
            position = max(ch.position for ch in existing_channels) + 1
        
        thread_config = {
            "default_auto_archive_duration": 10080,  # 7 days
            "default_thread_slowmode_delay": 0,
            "require_tag": require_tag,
            "available_tags": available_tags
        }
        
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
        
        exist_result = await session.execute(select(ChannelEntity).where(ChannelEntity.name == channel.name, ChannelEntity.category_id == channel.category_id))
        existing = exist_result.scalars().first()
        if existing:
            channel.id = existing.id
        saved_channel = await channel_repo.save_channel(channel)
        
        discord_channel = await channel_builder.create_channel(guild, saved_channel, session)
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