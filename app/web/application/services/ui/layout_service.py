from typing import Optional, Dict, Any
import logging

from app.shared.domain.repositories.ui.ui_layout_repository import UILayoutRepository
from app.shared.infrastructure.models.ui.ui_layout_entity import UILayoutEntity # For type hinting

logger = logging.getLogger(__name__)

class LayoutService:
    """
    Service layer for handling business logic related to UI layouts.
    """

    def __init__(self, layout_repository: UILayoutRepository):
        self.layout_repository = layout_repository

    async def get_user_layout(self, user_id: int, page_identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the layout data for a specific user and page.

        Args:
            user_id: The ID of the user.
            page_identifier: The unique identifier for the page.

        Returns:
            The layout data as a dictionary if found, otherwise None.
        """
        logger.debug(f"Attempting to get layout for user {user_id}, page {page_identifier}")
        layout_entity = await self.layout_repository.get_layout(user_id, page_identifier)
        if layout_entity:
            logger.debug(f"Layout found for user {user_id}, page {page_identifier}")
            return layout_entity.layout_data
        else:
            logger.debug(f"No layout found for user {user_id}, page {page_identifier}")
            return None

    async def save_user_layout(self, user_id: int, page_identifier: str, layout_data: Dict[str, Any]) -> bool:
        """
        Saves or updates the layout data for a specific user and page.
        Includes handling for the 'is_locked' status within layout_data.

        Args:
            user_id: The ID of the user.
            page_identifier: The unique identifier for the page.
            layout_data: The layout data to save (potentially including 'is_locked').

        Returns:
            True if saving was successful, False otherwise.
        """
        # Log whether the lock status is included
        if 'is_locked' in layout_data:
            logger.debug(f"Saving layout for user {user_id}, page {page_identifier}, including lock status: {layout_data.get('is_locked')}")
        else:
            logger.debug(f"Saving layout for user {user_id}, page {page_identifier}. Lock status ('is_locked') not provided in layout_data.")

        saved_entity = await self.layout_repository.save_layout(user_id, page_identifier, layout_data)
        if saved_entity:
            logger.info(f"Successfully saved layout for user {user_id}, page {page_identifier}")
            return True
        else:
            logger.error(f"Failed to save layout for user {user_id}, page {page_identifier}")
            return False

    async def reset_user_layout(self, user_id: int, page_identifier: str) -> bool:
        """
        Deletes (resets to default) the layout data for a specific user and page.

        Args:
            user_id: The ID of the user.
            page_identifier: The unique identifier for the page.

        Returns:
            True if deletion was successful, False otherwise.
        """
        logger.debug(f"Attempting to delete/reset layout for user {user_id}, page {page_identifier}")
        success = await self.layout_repository.delete_layout(user_id, page_identifier)
        if success:
            logger.info(f"Successfully deleted/reset layout for user {user_id}, page {page_identifier}")
        else:
            logger.error(f"Failed to delete/reset layout for user {user_id}, page {page_identifier}")
        return success
