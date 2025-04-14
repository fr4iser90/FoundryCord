from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.shared.domain.repositories.guild_templates import GuildTemplateCategoryPermissionRepository
from app.shared.infrastructure.models.guild_templates import GuildTemplateCategoryPermissionEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

class GuildTemplateCategoryPermissionRepositoryImpl(BaseRepositoryImpl[GuildTemplateCategoryPermissionEntity], GuildTemplateCategoryPermissionRepository):
    """SQLAlchemy implementation for guild template category permission repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(GuildTemplateCategoryPermissionEntity, session)

    async def create(
        self, 
        category_template_id: int, 
        role_name: str, 
        allow_permissions_bitfield: Optional[int],
        deny_permissions_bitfield: Optional[int]
    ) -> Optional[GuildTemplateCategoryPermissionEntity]:
        """Create a new category permission record within a guild template."""
        try:
            new_permission = self.model(
                category_template_id=category_template_id,
                role_name=role_name,
                allow_permissions_bitfield=allow_permissions_bitfield,
                deny_permissions_bitfield=deny_permissions_bitfield
            )
            self.session.add(new_permission)
            await self.session.flush()
            await self.session.refresh(new_permission)
            logger.debug(f"Created template category permission for role '{role_name}' on category template {category_template_id}")
            return new_permission
        except Exception as e:
            logger.error(f"Error creating template category permission for role '{role_name}' on category template {category_template_id}: {e}", exc_info=True)
            return None

    async def get_by_category_template_id(self, category_template_id: int) -> List[GuildTemplateCategoryPermissionEntity]:
        """Retrieve all permissions associated with a specific category template ID."""
        try:
            stmt = select(self.model).where(self.model.category_template_id == category_template_id)
            result = await self.session.execute(stmt)
            permissions = result.scalars().all()
            logger.debug(f"Found {len(permissions)} permissions for category_template_id {category_template_id}")
            return list(permissions)
        except Exception as e:
            logger.error(f"Error fetching permissions for category_template_id {category_template_id}: {e}", exc_info=True)
            return []
