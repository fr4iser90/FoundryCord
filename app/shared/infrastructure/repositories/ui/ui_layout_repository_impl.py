from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.shared.domain.repositories.ui.ui_layout_repository import UILayoutRepository
from app.shared.infrastructure.models.ui.ui_layout_entity import UILayoutEntity

logger = logging.getLogger(__name__)

class UILayoutRepositoryImpl(UILayoutRepository):
    """
    Concrete implementation of the UILayoutRepository interface using SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_layout(self, user_id: int, page_identifier: str) -> Optional[UILayoutEntity]:
        """Retrieves the layout for a specific user and page identifier."""
        try:
            result = await self.session.execute(
                select(UILayoutEntity)
                .filter_by(user_id=user_id, page_identifier=page_identifier)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving layout for user {user_id}, page {page_identifier}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving layout for user {user_id}, page {page_identifier}: {e}")
            return None

    async def save_layout(self, user_id: int, page_identifier: str, layout_data: Dict[str, Any]) -> Optional[UILayoutEntity]:
        """Saves or updates the layout for a specific user and page identifier."""
        try:
            # Try to get the existing layout
            existing_layout = await self.get_layout(user_id, page_identifier)

            if existing_layout:
                # Update existing layout
                existing_layout.layout_data = layout_data
                # updated_at is handled by onupdate
                self.session.add(existing_layout)
                await self.session.commit() # Commit the transaction
                logger.info(f"Updated layout for user {user_id}, page {page_identifier}")
                # Consider refreshing if needed after commit, depends on session config
                # await self.session.refresh(existing_layout)
                return existing_layout # Return the committed entity
            else:
                # Create new layout
                new_layout = UILayoutEntity(
                    user_id=user_id,
                    page_identifier=page_identifier,
                    layout_data=layout_data
                )
                self.session.add(new_layout)
                await self.session.commit() # Commit the transaction
                logger.info(f"Created new layout for user {user_id}, page {page_identifier}")
                # Consider refreshing if needed after commit
                # await self.session.refresh(new_layout)
                return new_layout # Return the committed entity

        except SQLAlchemyError as e:
            logger.error(f"Database error saving layout for user {user_id}, page {page_identifier}: {e}")
            await self.session.rollback() # Rollback on error
            return None
        except Exception as e:
            logger.error(f"Unexpected error saving layout for user {user_id}, page {page_identifier}: {e}")
            await self.session.rollback() # Rollback on error
            return None

    async def delete_layout(self, user_id: int, page_identifier: str) -> bool:
        """Deletes the layout for a specific user and page identifier."""
        try:
            layout_to_delete = await self.get_layout(user_id, page_identifier)
            if layout_to_delete:
                await self.session.delete(layout_to_delete)
                await self.session.commit() # Commit the deletion
                logger.info(f"Deleted layout for user {user_id}, page {page_identifier}")
                return True
            else:
                logger.info(f"Layout not found for deletion for user {user_id}, page {page_identifier}. No action taken.")
                return False
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting layout for user {user_id}, page {page_identifier}: {e}")
            await self.session.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting layout for user {user_id}, page {page_identifier}: {e}")
            await self.session.rollback()
            return False
