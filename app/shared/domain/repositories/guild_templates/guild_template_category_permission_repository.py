from abc import ABC, abstractmethod
from typing import Optional
# Import the entity
from app.shared.infrastructure.models.guild_templates.guild_template_category_permission_entity import GuildTemplateCategoryPermissionEntity

class GuildTemplateCategoryPermissionRepository(ABC):
    """Interface for guild template category permission repository."""

    @abstractmethod
    async def create(
        self, 
        category_template_id: int, 
        role_name: str, 
        allow_permissions_bitfield: Optional[int],
        deny_permissions_bitfield: Optional[int]
    ) -> Optional[GuildTemplateCategoryPermissionEntity]:
        """Create a new category permission record within a guild template."""
        pass
