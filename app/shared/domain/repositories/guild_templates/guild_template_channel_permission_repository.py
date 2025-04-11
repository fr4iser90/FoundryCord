from abc import ABC, abstractmethod
from typing import Optional
# Import the entity
from app.shared.infrastructure.models.guild_templates.guild_template_channel_permission_entity import GuildTemplateChannelPermissionEntity

class GuildTemplateChannelPermissionRepository(ABC):
    """Interface for guild template channel permission repository."""

    @abstractmethod
    async def create(
        self, 
        channel_template_id: int, 
        role_name: str, 
        allow_permissions_bitfield: Optional[int],
        deny_permissions_bitfield: Optional[int]
    ) -> Optional[GuildTemplateChannelPermissionEntity]:
        """Create a new channel permission record within a guild template."""
        pass
