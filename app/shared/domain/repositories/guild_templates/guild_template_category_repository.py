from abc import ABC, abstractmethod
from typing import Optional
# Import the entity
from app.shared.infrastructure.models.guild_templates.guild_template_category_entity import GuildTemplateCategoryEntity

class GuildTemplateCategoryRepository(ABC):
    """Interface for guild template category repository."""

    @abstractmethod
    async def create(self, guild_template_id: int, category_name: str, position: int) -> Optional[GuildTemplateCategoryEntity]:
        """Create a new category record within a guild template."""
        pass
