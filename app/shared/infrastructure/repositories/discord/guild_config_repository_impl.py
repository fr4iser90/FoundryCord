from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.models.discord.entities.guild_config_entity import GuildConfigEntity
from app.shared.domain.repositories.discord.guild_config_repository import GuildConfigRepository
from typing import Optional, List, Dict, Any
import json

class GuildConfigRepositoryImpl(GuildConfigRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_guild_id(self, guild_id: str) -> Optional[GuildConfigEntity]:
        """Get configuration for a specific guild"""
        result = await self.session.execute(
            select(GuildConfigEntity).where(GuildConfigEntity.guild_id == guild_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[GuildConfigEntity]:
        """Get configurations for all guilds"""
        result = await self.session.execute(select(GuildConfigEntity))
        return result.scalars().all()
    
    async def create_or_update(self, guild_id: str, guild_name: str,
                              features: Dict[str, bool] = None,
                              settings: Dict[str, Any] = None) -> GuildConfigEntity:
        """Create or update guild configuration"""
        # First check if config exists
        config = await self.get_by_guild_id(guild_id)

        if not config:
            config = GuildConfigEntity(
                guild_id=guild_id,
                guild_name=guild_name
            )
            # Apply default values from model if new
            if features:
                 config.enable_dashboard = features.get('dashboard', False)
                 config.enable_tasks = features.get('tasks', False)
                 config.enable_services = features.get('services', False)

        else:
            # Ensure name is updated if config already exists
            config.guild_name = guild_name
            # Update existing features if provided
            if features:
                 config.enable_dashboard = features.get('dashboard', config.enable_dashboard)
                 config.enable_tasks = features.get('tasks', config.enable_tasks)
                 config.enable_services = features.get('services', config.enable_services)

        # Update settings if provided
        if settings:
            config.settings = json.dumps(settings)

        self.session.add(config)
        await self.session.commit()
        # Refresh the object to get the latest state from DB, including defaults
        await self.session.refresh(config)
        return config
        
    async def delete(self, config: GuildConfigEntity) -> None:
        """Delete a guild configuration"""
        await self.session.delete(config)
        await self.session.commit()