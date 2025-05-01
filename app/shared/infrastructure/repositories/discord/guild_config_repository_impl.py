from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.models.discord.entities.guild_config_entity import GuildConfigEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from app.shared.domain.repositories.discord.guild_config_repository import GuildConfigRepository
from typing import Optional, List, Dict, Any
import json

class GuildConfigRepositoryImpl(BaseRepositoryImpl[GuildConfigEntity], GuildConfigRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(GuildConfigEntity, session)
    
    async def get_by_guild_id(self, guild_id: str) -> Optional[GuildConfigEntity]:
        """Get configuration for a specific guild"""
        result = await self.session.execute(
            select(self.model).where(self.model.guild_id == guild_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[GuildConfigEntity]:
        """Get configurations for all guilds"""
        result = await self.session.execute(select(self.model))
        return result.scalars().all()
    
    async def create_or_update(self, guild_id: str, guild_name: str,
                              features: Dict[str, bool] = None,
                              settings: Dict[str, Any] = None,
                              active_template_id: Optional[int] = None,
                              template_delete_unmanaged: Optional[bool] = None) -> GuildConfigEntity:
        """Create or update guild configuration, now handling template_delete_unmanaged."""
        config = await self.get_by_guild_id(guild_id)

        if not config:
            # Creating new config
            config = GuildConfigEntity(
                guild_id=guild_id,
                guild_name=guild_name
            )
            # Apply features if provided
            if features:
                 config.enable_dashboard = features.get('dashboard', False)
                 config.enable_tasks = features.get('tasks', False)
                 config.enable_services = features.get('services', False)
            # Set active template if provided
            if active_template_id is not None:
                config.active_template_id = active_template_id
            # SET template_delete_unmanaged IF PROVIDED FOR NEW
            if template_delete_unmanaged is not None:
                config.template_delete_unmanaged = template_delete_unmanaged
            # If not provided, the model/db default (False) will be used
            # END SET

        else:
            # Updating existing config
            config.guild_name = guild_name # Ensure name is updated
            # Update features if provided
            if features:
                 config.enable_dashboard = features.get('dashboard', config.enable_dashboard)
                 config.enable_tasks = features.get('tasks', config.enable_tasks)
                 config.enable_services = features.get('services', config.enable_services)
            # Update active template if provided
            if active_template_id is not None:
                config.active_template_id = active_template_id
            # UPDATE template_delete_unmanaged IF PROVIDED FOR EXISTING
            if template_delete_unmanaged is not None:
                config.template_delete_unmanaged = template_delete_unmanaged
            # END UPDATE

        # Update settings if provided
        if settings:
            config.settings = json.dumps(settings)

        self.session.add(config)
        # Caller might expect commit, so keeping add() only might be correct here.
        # Let's add flush/refresh for consistency, assuming caller doesn't commit.
        await self.session.flush()
        await self.session.refresh(config)
        return config
        
    async def update_template_delete_unmanaged(self, guild_id: str, delete_unmanaged: bool) -> bool:
        """Update the template_delete_unmanaged flag for a specific guild."""
        config = await self.get_by_guild_id(guild_id)
        if not config:
            return False # Guild config not found
        
        config.template_delete_unmanaged = delete_unmanaged
        self.session.add(config)
        # Add flush to ensure change is sent before potential commit by caller
        await self.session.flush()
        return True

    async def delete(self, config: GuildConfigEntity) -> None:
        """Delete a guild configuration"""
        await super().delete(config)