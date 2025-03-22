from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.database.models.discord.guild_config import GuildConfig
from typing import Optional, List, Dict, Any
import json

class GuildConfigRepositoryImpl:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_guild_id(self, guild_id: str) -> Optional[GuildConfig]:
        """Get configuration for a specific guild"""
        result = await self.session.execute(
            select(GuildConfig).where(GuildConfig.guild_id == guild_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[GuildConfig]:
        """Get configurations for all guilds"""
        result = await self.session.execute(select(GuildConfig))
        return result.scalars().all()
    
    async def create_or_update(self, guild_id: str, guild_name: str, 
                              features: Dict[str, bool] = None, 
                              settings: Dict[str, Any] = None) -> GuildConfig:
        """Create or update guild configuration"""
        config = await self.get_by_guild_id(guild_id)
        
        if not config:
            config = GuildConfig(
                guild_id=guild_id,
                guild_name=guild_name
            )
        
        # Update features if provided
        if features:
            for feature, enabled in features.items():
                if hasattr(config, f"enable_{feature}"):
                    setattr(config, f"enable_{feature}", enabled)
        
        # Update settings if provided
        if settings:
            config.settings = json.dumps(settings)
        
        self.session.add(config)
        await self.session.commit()
        return config
        
    async def delete(self, config: GuildConfig) -> None:
        """Delete a guild configuration"""
        await self.session.delete(config)
        await self.session.commit()