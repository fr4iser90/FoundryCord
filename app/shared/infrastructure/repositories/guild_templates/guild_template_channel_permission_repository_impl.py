from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.shared.domain.repositories.guild_templates import GuildTemplateChannelPermissionRepository
from app.shared.infrastructure.models.guild_templates import GuildTemplateChannelPermissionEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

class GuildTemplateChannelPermissionRepositoryImpl(BaseRepositoryImpl[GuildTemplateChannelPermissionEntity], GuildTemplateChannelPermissionRepository):
    """SQLAlchemy implementation for guild template channel permission repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(GuildTemplateChannelPermissionEntity, session)

    async def create(
        self, 
        channel_template_id: int, 
        role_name: str, 
        allow_permissions_bitfield: Optional[int],
        deny_permissions_bitfield: Optional[int]
    ) -> Optional[GuildTemplateChannelPermissionEntity]:
        """Create a new channel permission record within a guild template."""
        try:
            new_permission = self.model(
                channel_template_id=channel_template_id,
                role_name=role_name,
                allow_permissions_bitfield=allow_permissions_bitfield,
                deny_permissions_bitfield=deny_permissions_bitfield
            )
            self.session.add(new_permission)
            await self.session.flush()
            await self.session.refresh(new_permission)
            logger.debug(f"Created template channel permission for role '{role_name}' on channel template {channel_template_id}")
            return new_permission
        except Exception as e:
            logger.error(f"Error creating template channel permission for role '{role_name}' on channel template {channel_template_id}: {e}", exc_info=True)
            return None
