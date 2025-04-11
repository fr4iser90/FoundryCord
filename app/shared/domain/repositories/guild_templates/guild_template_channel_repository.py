from abc import ABC, abstractmethod
from typing import Optional
# Import the entity
from app.shared.infrastructure.models.guild_templates.guild_template_channel_entity import GuildTemplateChannelEntity

class GuildTemplateChannelRepository(ABC):
    """Interface for guild template channel repository."""

    @abstractmethod
    async def create(
        self, 
        guild_template_id: int, 
        channel_name: str, 
        channel_type: str, 
        position: int, 
        parent_category_template_id: Optional[int],
        topic: Optional[str] = None,
        is_nsfw: bool = False,
        slowmode_delay: int = 0
    ) -> Optional[GuildTemplateChannelEntity]:
        """Create a new channel record within a guild template."""
        pass
