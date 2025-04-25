from typing import Optional, List
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

    async def get_by_id(self, template_id: int) -> Optional[GuildTemplateEntity]:
        """Retrieve a guild template by its primary key."""
        try:
            # Correct way to get by primary key using session.get()
            entity = await self.session.get(self.model, template_id) 
            if entity:
                logger.debug(f"Retrieved template {template_id} by ID.")
            else:
                logger.debug(f"Template {template_id} not found by ID.")
            return entity
        except Exception as e:
            logger.error(f"Error retrieving guild template by id {template_id}: {e}", exc_info=True)
            return None

    async def get_by_name_and_creator(self, template_name: str, creator_user_id: int) -> Optional[GuildTemplateEntity]:
        """Get a guild template by its name and creator user ID."""
        try:
            stmt = select(self.model).where(
                self.model.template_name == template_name,
                self.model.creator_user_id == creator_user_id 
            )
            # Optional: Add other conditions? e.g., only check non-initial snapshots?
            # stmt = stmt.where(self.model.guild_id.is_(None)) # Example: only check user-created, non-snapshot templates

            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if entity:
                logger.debug(f"Found guild template by name: '{template_name}' and creator: {creator_user_id} (ID: {entity.id})")
            else:
                logger.debug(f"No guild template found with name: '{template_name}' for creator: {creator_user_id}")
            return entity
        except Exception as e:
            logger.error(f"Error retrieving guild template by name '{template_name}' and creator {creator_user_id}: {e}", exc_info=True)
            return None

    async def create(
        self, 
        template_name: str,
        creator_user_id: Optional[int] = None,
        guild_id: Optional[str] = None, 
        template_description: Optional[str] = None,
        is_shared: bool = False,
        structure_version: Optional[str] = None
        # Add other fields from GuildTemplateEntity as needed
    ) -> Optional[GuildTemplateEntity]:
        """Create a new guild template record.

        Handles initial snapshots (guild_id set, creator_user_id=None) 
        and user-created templates (creator_user_id set, guild_id=None or source)."""
        try:
            # --- Duplicate Check (User-Saved Templates) ---
            # Check for duplicate template name for the same creator
            if creator_user_id:
                existing_by_name = await self.get_by_name_and_creator(template_name, creator_user_id)
                if existing_by_name:
                    logger.warning(f"User {creator_user_id} attempted to create duplicate template name '{template_name}'.")
                    # Raise an error or return None to indicate failure due to duplication
                    # Returning None for now, service layer should handle it.
                    return None 
            # --- End Duplicate Check ---

            new_template = self.model(
                guild_id=guild_id,
                template_name=template_name,
                template_description=template_description,
                creator_user_id=creator_user_id,
                is_shared=is_shared,
                # structure_version=structure_version # Uncomment if structure_version is added to model
                # Set defaults for other fields if needed, though DB defaults often handle this
                is_active=True 
            )

            self.session.add(new_template)
            await self.session.flush() # Use flush to get the ID before commit if needed elsewhere
            await self.session.refresh(new_template)
            logger.info(f"Created new guild template (ID: {new_template.id}, Name: '{new_template.template_name}')")
            return new_template
        except Exception as e:
            logger.error(f"Error creating guild template '{template_name}': {e}", exc_info=True)
            # Consider rolling back if part of a larger transaction
            # await self.session.rollback()
            return None

    async def delete(self, entity: GuildTemplateEntity) -> bool:
        """Delete a guild template entity."""
        try:
            await self.session.delete(entity)
            await self.session.flush() # Use flush to ensure deletion action is sent before commit
            logger.info(f"Deleted guild template with ID: {entity.id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting guild template with ID {entity.id}: {e}", exc_info=True)
            # Consider rolling back if part of a larger transaction
            # await self.session.rollback()
            return False

    # --- NEW METHOD --- 
    async def get_shared_templates(self) -> List[GuildTemplateEntity]:
        """Retrieves all guild templates marked as shared."""
        try:
            # Assuming GuildTemplateEntity has an 'is_shared' boolean field
            stmt = select(self.model).where(self.model.is_shared == True).order_by(self.model.template_name)
            result = await self.session.execute(stmt)
            entities = result.scalars().all()
            logger.debug(f"Found {len(entities)} shared templates.")
            return entities
        except Exception as e:
            # Log the specific error
            logger.error(f"Error retrieving shared guild templates: {e}", exc_info=True)
            # Return empty list or raise the exception depending on desired handling
            # Raising might be better to signal a DB issue upstream.
            raise # Re-raise the exception
