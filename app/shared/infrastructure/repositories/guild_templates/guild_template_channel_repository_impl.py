from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.shared.domain.repositories.guild_templates import GuildTemplateChannelRepository
from app.shared.infrastructure.models.guild_templates import GuildTemplateChannelEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from app.shared.interfaces.logging.api import get_db_logger

logger = get_db_logger()

class GuildTemplateChannelRepositoryImpl(BaseRepositoryImpl[GuildTemplateChannelEntity], GuildTemplateChannelRepository):
    """SQLAlchemy implementation for guild template channel repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(GuildTemplateChannelEntity, session)

    async def get_by_id(self, template_id: int) -> Optional[GuildTemplateChannelEntity]:
        """Retrieve a guild template channel by its primary key."""
        try:
            # Use session.get() for efficient primary key lookup
            entity = await self.session.get(self.model, template_id) 
            if entity:
                logger.debug(f"Retrieved template channel {template_id} by ID.")
            else:
                logger.debug(f"Template channel {template_id} not found by ID.")
            return entity
        except Exception as e:
            logger.error(f"Error retrieving guild template channel by id {template_id}: {e}", exc_info=True)
            return None

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

    async def get_by_template_id(self, guild_template_id: int) -> List[GuildTemplateChannelEntity]:
        """Retrieve all channels associated with a specific guild template ID."""
        try:
            stmt = select(self.model).where(self.model.guild_template_id == guild_template_id).order_by(self.model.position)
            result = await self.session.execute(stmt)
            channels = result.scalars().all()
            logger.debug(f"Found {len(channels)} channels for template_id {guild_template_id}")
            return list(channels)
        except Exception as e:
            logger.error(f"Error fetching channels for template_id {guild_template_id}: {e}", exc_info=True)
            return []
