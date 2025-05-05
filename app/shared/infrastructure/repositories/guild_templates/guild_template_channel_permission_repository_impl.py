from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.shared.domain.repositories.guild_templates import GuildTemplateChannelPermissionRepository
from app.shared.infrastructure.models.guild_templates import GuildTemplateChannelPermissionEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from app.shared.interfaces.logging.api import get_db_logger

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

    async def get_by_channel_template_id(self, channel_template_id: int) -> List[GuildTemplateChannelPermissionEntity]:
        """Retrieves all permission entities associated with a specific channel template ID."""
        try:
            stmt = select(self.model).where(self.model.channel_template_id == channel_template_id)
            result = await self.session.execute(stmt)
            entities = result.scalars().all()
            logger.debug(f"Found {len(entities)} permissions for channel template ID {channel_template_id}.")
            return entities
        except Exception as e:
            logger.error(f"Error retrieving permissions for channel template ID {channel_template_id}: {e}", exc_info=True)
            raise # Re-raise the exception to be handled by the service layer
