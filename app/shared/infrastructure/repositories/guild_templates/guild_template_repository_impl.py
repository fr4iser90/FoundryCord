from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # If needed for relationships later

from app.shared.domain.repositories.guild_templates import GuildTemplateRepository
from app.shared.infrastructure.models.guild_templates import GuildTemplateEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl # Assuming a base class exists
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

class GuildTemplateRepositoryImpl(BaseRepositoryImpl[GuildTemplateEntity], GuildTemplateRepository):
    """SQLAlchemy implementation for guild template repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(GuildTemplateEntity, session)

    async def get_by_guild_id(self, guild_id: str) -> Optional[GuildTemplateEntity]:
        """Get a guild template by its Discord Guild ID."""
        try:
            stmt = select(self.model).where(self.model.guild_id == guild_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if entity:
                logger.debug(f"Found guild template for guild_id: {guild_id}")
            else:
                logger.debug(f"No guild template found for guild_id: {guild_id}")
            return entity
        except Exception as e:
            logger.error(f"Error retrieving guild template by guild_id {guild_id}: {e}", exc_info=True)
            return None

    async def create(self, guild_id: str, template_name: str) -> Optional[GuildTemplateEntity]:
        """Create a new guild template record."""
        try:
            # Check if one already exists for this guild_id
            existing = await self.get_by_guild_id(guild_id)
            if existing:
                logger.warning(f"Attempted to create duplicate guild template for guild_id: {guild_id}")
                return existing # Or maybe raise an error?

            new_template = self.model(guild_id=guild_id, template_name=template_name)
            self.session.add(new_template)
            await self.session.flush() # Use flush to get the ID before commit if needed elsewhere
            await self.session.refresh(new_template)
            logger.info(f"Created new guild template (ID: {new_template.id}) for guild_id: {guild_id}")
            return new_template
        except Exception as e:
            logger.error(f"Error creating guild template for guild_id {guild_id}: {e}", exc_info=True)
            # Consider rolling back if part of a larger transaction
            # await self.session.rollback()
            return None
