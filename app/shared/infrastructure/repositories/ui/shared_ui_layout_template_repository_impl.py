from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sql_update # Use alias to avoid conflict with method name
from sqlalchemy import delete as sql_delete # Use alias
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Optional, List, Dict, Any
import logging

# Import the interface and the model
from app.shared.domain.repositories.ui.shared_ui_layout_template_repository import SharedUILayoutTemplateRepository
from app.shared.infrastructure.models.ui import SharedUILayoutTemplateEntity

logger = logging.getLogger(__name__)

class SharedUILayoutTemplateRepositoryImpl(SharedUILayoutTemplateRepository):
    """
    Concrete implementation of the SharedUILayoutTemplateRepository using SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, 
        name: str, 
        layout_data: Dict[str, Any], 
        creator_user_id: Optional[int] = None, 
        description: Optional[str] = None
    ) -> Optional[SharedUILayoutTemplateEntity]:
        """Creates a new shared layout template."""
        try:
            new_template = SharedUILayoutTemplateEntity(
                name=name,
                description=description,
                layout_data=layout_data,
                creator_user_id=creator_user_id
            )
            self.session.add(new_template)
            await self.session.commit()
            await self.session.refresh(new_template) # Refresh to get ID, created_at etc.
            logger.info(f"Created shared layout template '{name}' (ID: {new_template.id})")
            return new_template
        except IntegrityError as e: # Handles potential unique constraint violation on name
            logger.error(f"Failed to create shared template '{name}' due to integrity error (likely duplicate name): {e}")
            await self.session.rollback()
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error creating shared template '{name}': {e}")
            await self.session.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating shared template '{name}': {e}")
            await self.session.rollback()
            return None

    async def get_by_id(self, template_id: int) -> Optional[SharedUILayoutTemplateEntity]:
        """Retrieves a shared template by its unique ID."""
        try:
            result = await self.session.execute(
                select(SharedUILayoutTemplateEntity).filter_by(id=template_id)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving shared template ID {template_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving shared template ID {template_id}: {e}")
            return None

    async def get_by_name(self, name: str) -> Optional[SharedUILayoutTemplateEntity]:
        """Retrieves a shared template by its unique name."""
        try:
            result = await self.session.execute(
                select(SharedUILayoutTemplateEntity).filter_by(name=name)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving shared template by name '{name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving shared template by name '{name}': {e}")
            return None

    async def get_all(self) -> List[SharedUILayoutTemplateEntity]:
        """Retrieves all shared layout templates."""
        try:
            result = await self.session.execute(select(SharedUILayoutTemplateEntity).order_by(SharedUILayoutTemplateEntity.name))
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving all shared templates: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving all shared templates: {e}")
            return []

    async def update(
        self, 
        template_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        layout_data: Optional[Dict[str, Any]] = None
    ) -> Optional[SharedUILayoutTemplateEntity]:
        """Updates an existing shared layout template."""
        try:
            # Fetch the existing template first
            template = await self.get_by_id(template_id)
            if not template:
                logger.warning(f"Attempted to update non-existent shared template ID {template_id}")
                return None

            update_values = {}
            if name is not None:
                update_values['name'] = name
            if description is not None:
                update_values['description'] = description
            if layout_data is not None:
                update_values['layout_data'] = layout_data
            
            if not update_values:
                logger.info(f"No update values provided for shared template ID {template_id}. No action taken.")
                return template # Return the unchanged template

            # Perform the update
            await self.session.execute(
                sql_update(SharedUILayoutTemplateEntity)
                .where(SharedUILayoutTemplateEntity.id == template_id)
                .values(**update_values)
            )
            await self.session.commit()
            await self.session.refresh(template) # Refresh to get updated state
            logger.info(f"Updated shared layout template ID {template_id}")
            return template
        except IntegrityError as e:
             logger.error(f"Failed to update shared template ID {template_id} due to integrity error (likely duplicate name if changed): {e}")
             await self.session.rollback()
             return None
        except SQLAlchemyError as e:
            logger.error(f"Database error updating shared template ID {template_id}: {e}")
            await self.session.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error updating shared template ID {template_id}: {e}")
            await self.session.rollback()
            return None

    async def delete(self, template_id: int) -> bool:
        """Deletes a shared layout template by its ID."""
        try:
            result = await self.session.execute(
                sql_delete(SharedUILayoutTemplateEntity)
                .where(SharedUILayoutTemplateEntity.id == template_id)
            )
            await self.session.commit()
            
            if result.rowcount > 0:
                logger.info(f"Deleted shared layout template ID {template_id}")
                return True
            else:
                logger.warning(f"Shared template ID {template_id} not found for deletion.")
                return False # Explicitly false if not found
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting shared template ID {template_id}: {e}")
            await self.session.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting shared template ID {template_id}: {e}")
            await self.session.rollback()
            return False
