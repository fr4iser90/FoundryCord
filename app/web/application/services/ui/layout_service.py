from typing import Optional, Dict, Any, List
import logging
from datetime import datetime # Import needed for list_templates

# --- Only need the user-specific layout repository --- 
from app.shared.domain.repositories.ui.ui_layout_repository import UILayoutRepository
# from app.shared.domain.repositories.ui.shared_ui_layout_template_repository import SharedUILayoutTemplateRepository

from app.shared.infrastructure.models.ui.ui_layout_entity import UILayoutEntity # For type hinting


# Import the necessary schemas
from app.web.interfaces.api.rest.v1.schemas.ui_layout_schemas import (
    UILayoutResponseSchema,
    UILayoutSaveSchema,
    # Remove template-related schemas
    # LayoutTemplateInfoSchema,
    # LayoutTemplateListResponse,
    GridstackItem 
)

logger = logging.getLogger(__name__)

class LayoutService:
    """
    Service layer for handling business logic related to user-specific UI layouts.
    """

    def __init__(self,
        layout_repository: UILayoutRepository
        # Remove shared repo dependency
        # shared_layout_repository: SharedUILayoutTemplateRepository 
    ):
        self.layout_repository = layout_repository
        # self.shared_layout_repository = shared_layout_repository

    async def get_layout(self, user_id: int, page_identifier: str) -> Optional[UILayoutResponseSchema]:
        """
        Retrieves the layout data for a specific user and page, formatted for API response.
        """
        logger.debug(f"Attempting to get saved layout for user {user_id}, page {page_identifier}")
        layout_entity = await self.layout_repository.get_layout(user_id, page_identifier)
        
        if layout_entity and isinstance(layout_entity.layout_data, dict):
            logger.debug(f"Layout found for user {user_id}, page {page_identifier}. Formatting response.")
            try:
                # Extract layout and lock status from the stored JSON
                grid_items_data = layout_entity.layout_data.get('layout', [])
                is_locked = layout_entity.layout_data.get('is_locked', False)
                
                # Validate/parse grid items (optional but good practice)
                parsed_items = [GridstackItem(**item) for item in grid_items_data]
                
                return UILayoutResponseSchema(
                    page_identifier=layout_entity.page_identifier,
                    layout=parsed_items,
                    is_locked=is_locked,
                    # Name is not currently part of user-specific layout saving
                    # name=layout_entity.layout_data.get('name'), 
                    updated_at=layout_entity.updated_at
                )
            except Exception as e: # Catch potential validation errors
                logger.error(f"Error processing layout data for user {user_id}, page {page_identifier}: {e}", exc_info=True)
                return None # Return None if data format is invalid
        else:
            logger.debug(f"No saved layout found or layout_data is not a dict for user {user_id}, page {page_identifier}")
            return None

    async def save_layout(self, user_id: int, page_identifier: str, data: UILayoutSaveSchema) -> bool:
        """
        Saves or updates the layout data for a specific user and page.
        The data includes the grid layout and the lock state.
        """
        # Prepare the dictionary to be saved as JSON
        layout_data_to_save = {
            "layout": [item.model_dump() for item in data.layout],
            "is_locked": data.is_locked,
        }
        logger.debug(f"Saving layout for user {user_id}, page {page_identifier}, lock status: {data.is_locked}")
        try:
            saved_entity = await self.layout_repository.save_layout(
                user_id=user_id,
                page_identifier=page_identifier,
                layout_data=layout_data_to_save
            )
            return bool(saved_entity) # Return True if save was successful
        except Exception as e:
             logger.error(f"Failed to save layout for user {user_id}, page {page_identifier}: {e}", exc_info=True)
             return False

    # --- REMOVED list_templates method --- 

    async def delete_layout(self, user_id: int, page_identifier: str) -> bool:
        """
        Deletes the layout data for a specific user and page.
        """
        logger.debug(f"Attempting to delete user layout for user {user_id}, page {page_identifier}")
        try:
            success = await self.layout_repository.delete_layout(user_id, page_identifier)
            if success:
                logger.info(f"Successfully deleted user layout for user {user_id}, page {page_identifier}")
            # Repository logs if not found, no need to log again here
            return success
        except Exception as e:
            logger.error(f"Failed to delete layout for user {user_id}, page {page_identifier}: {e}", exc_info=True)
            return False

    # --- REMOVED share_layout method --- 
