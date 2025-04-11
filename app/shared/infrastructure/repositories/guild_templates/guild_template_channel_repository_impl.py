from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.shared.domain.repositories.guild_templates import GuildTemplateChannelRepository
from app.shared.infrastructure.models.guild_templates import GuildTemplateChannelEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

class GuildTemplateChannelRepositoryImpl(BaseRepositoryImpl[GuildTemplateChannelEntity], GuildTemplateChannelRepository):
    """SQLAlchemy implementation for guild template channel repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(GuildTemplateChannelEntity, session)

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
        try:
            new_channel = self.model(
                guild_template_id=guild_template_id,
                channel_name=channel_name,
                channel_type=channel_type,
                position=position,
                parent_category_template_id=parent_category_template_id,
                topic=topic,
                is_nsfw=is_nsfw,
                slowmode_delay=slowmode_delay
            )
            self.session.add(new_channel)
            await self.session.flush()
            await self.session.refresh(new_channel)
            logger.debug(f"Created template channel '{channel_name}' (ID: {new_channel.id}) for template {guild_template_id}")
            return new_channel
        except Exception as e:
            logger.error(f"Error creating template channel '{channel_name}' for template {guild_template_id}: {e}", exc_info=True)
            return None
