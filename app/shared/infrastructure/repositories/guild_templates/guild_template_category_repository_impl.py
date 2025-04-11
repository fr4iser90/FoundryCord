from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.shared.domain.repositories.guild_templates import GuildTemplateCategoryRepository
from app.shared.infrastructure.models.guild_templates import GuildTemplateCategoryEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

class GuildTemplateCategoryRepositoryImpl(BaseRepositoryImpl[GuildTemplateCategoryEntity], GuildTemplateCategoryRepository):
    """SQLAlchemy implementation for guild template category repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(GuildTemplateCategoryEntity, session)

    async def create(self, guild_template_id: int, category_name: str, position: int) -> Optional[GuildTemplateCategoryEntity]:
        """Create a new category record within a guild template."""
        try:
            new_category = self.model(
                guild_template_id=guild_template_id, 
                category_name=category_name, 
                position=position
            )
            self.session.add(new_category)
            await self.session.flush()
            await self.session.refresh(new_category)
            logger.debug(f"Created template category '{category_name}' (ID: {new_category.id}) for template {guild_template_id}")
            return new_category
        except Exception as e:
            logger.error(f"Error creating template category '{category_name}' for template {guild_template_id}: {e}", exc_info=True)
            return None
