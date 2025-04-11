from abc import ABC, abstractmethod
from typing import Optional
# Import the entity from the correct location
from app.shared.infrastructure.models.guild_templates.guild_template_entity import GuildTemplateEntity

class GuildTemplateRepository(ABC):
    """Interface for guild template repository."""

    @abstractmethod
    async def get_by_guild_id(self, guild_id: str) -> Optional[GuildTemplateEntity]:
        """Get a guild template by its Discord Guild ID."""
        pass

    @abstractmethod
    async def create(self, guild_id: str, template_name: str) -> Optional[GuildTemplateEntity]:
        """Create a new guild template record."""
        pass
