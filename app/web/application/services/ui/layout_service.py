from typing import Optional, Dict, Any, List
import logging

from app.shared.domain.repositories.ui.ui_layout_repository import UILayoutRepository
from app.shared.infrastructure.models.ui.ui_layout_entity import UILayoutEntity # For type hinting
# Import the necessary schemas
from app.web.interfaces.api.rest.v1.schemas.ui_layout_schemas import (
    UILayoutResponseSchema,
    UILayoutSaveSchema,
    LayoutTemplateInfoSchema,
    LayoutTemplateListResponse,
    GridstackItem # Potentially needed if manipulating layout list
)

logger = logging.getLogger(__name__)

class LayoutService:
    """
    Service layer for handling business logic related to UI layouts.
    """

    def __init__(self, layout_repository: UILayoutRepository):
        self.layout_repository = layout_repository

    async def get_layout(self, user_id: int, page_identifier: str) -> Optional[UILayoutResponseSchema]:
        """
        Retrieves the layout data for a specific user and page, formatted for API response.

        Args:
            user_id: The ID of the user.
            page_identifier: The unique identifier for the page.

        Returns:
            A UILayoutResponseSchema object if found, otherwise None.
        """
        logger.debug(f"Attempting to get layout for user {user_id}, page {page_identifier}")
        layout_entity = await self.layout_repository.get_layout(user_id, page_identifier)
        if layout_entity and isinstance(layout_entity.layout_data, dict):
            logger.debug(f"Layout found for user {user_id}, page {page_identifier}. Formatting response.")
            try:
                # Extract data, assuming layout_data contains 'layout' list and 'is_locked' bool
                grid_items_data = layout_entity.layout_data.get('layout', [])
                is_locked = layout_entity.layout_data.get('is_locked', False) # Default to False if missing

                # Validate and parse grid items (optional but good practice)
                parsed_items = [GridstackItem(**item) for item in grid_items_data]

                return UILayoutResponseSchema(
                    page_identifier=layout_entity.page_identifier,
                    layout=parsed_items,
                    is_locked=is_locked,
                    name=layout_entity.layout_data.get('name'), # Attempt to get name if stored
                    updated_at=layout_entity.updated_at
                )
            except Exception as e: # Catch potential validation or key errors
                logger.error(f"Error processing layout data for user {user_id}, page {page_identifier}: {e}", exc_info=True)
                return None # Or raise a specific service layer exception
        else:
            logger.debug(f"No layout found or layout_data is not a dict for user {user_id}, page {page_identifier}")
            return None

    async def save_layout(self, user_id: int, page_identifier: str, data: UILayoutSaveSchema) -> bool:
        """
        Saves or updates the layout data for a specific user and page.

        Args:
            user_id: The ID of the user.
            page_identifier: The unique identifier for the page.
            data: The UILayoutSaveSchema containing layout items and lock state.

        Returns:
            True if saving was successful, False otherwise.
        """
        # Prepare the dictionary to be saved in the JSON column
        layout_data_to_save = {
            "layout": [item.model_dump() for item in data.layout],
            "is_locked": data.is_locked,
            # "name": data.name # Include if name is added to UILayoutSaveSchema
        }

        logger.debug(f"Saving layout for user {user_id}, page {page_identifier}, lock status: {data.is_locked}")
        try:
            saved_entity = await self.layout_repository.save_layout(
                user_id=user_id,
                page_identifier=page_identifier,
                layout_data=layout_data_to_save
            )
            if saved_entity:
                logger.info(f"Successfully saved layout for user {user_id}, page {page_identifier}")
                return True
            else:
                # This case might not happen if save_layout raises exceptions on failure
                logger.error(f"Repository returned no entity after saving layout for user {user_id}, page {page_identifier}")
                return False
        except Exception as e:
             logger.error(f"Failed to save layout for user {user_id}, page {page_identifier}: {e}", exc_info=True)
             return False

    async def list_templates(self, user_id: int, guild_id: Optional[str] = None, scope: Optional[str] = None) -> LayoutTemplateListResponse:
        """
        Lists available layout templates based on criteria, including the initial snapshot.

        Args:
            user_id: The ID of the user making the request.
            guild_id: Optional guild ID filter. Used to construct the initial snapshot ID.
            scope: Optional scope filter ('user', 'guild', 'shared').

        Returns:
            A LayoutTemplateListResponse containing the list of templates.
        """
        logger.debug(f"Listing templates for user {user_id}, guild_id={guild_id}, scope={scope}")
        templates_info: List[LayoutTemplateInfoSchema] = []
        
        # 1. Add the Initial Snapshot representation if guild_id is provided
        if guild_id:
            # TODO: Fetch actual guild name or use a more robust way to get initial snapshot info
            initial_snapshot_name = f"Initial Snapshot (Guild: {guild_id})" 
            initial_snapshot_id = f"guild-designer-{guild_id}" # Assuming this is the identifier
            
            # Use a recent timestamp, ideally reflecting actual snapshot time if available
            from datetime import datetime # Import here or at top level
            initial_snapshot_template = LayoutTemplateInfoSchema(
                layout_id=initial_snapshot_id,
                name=initial_snapshot_name,
                is_shared=False, # Initial snapshot is typically not 'shared' in the template sense
                is_initial=True, # Mark this as the initial one
                updated_at=datetime.utcnow() # Placeholder timestamp
            )
            templates_info.append(initial_snapshot_template)
            logger.debug(f"Added initial snapshot representation for guild {guild_id}")

        # 2. Fetch user-saved layout entities from the repository
        try:
            # Note: Filtering by guild_id/scope in the repository is still pending implementation
            layout_entities = await self.layout_repository.list_layouts(user_id, guild_id, scope)
            
            # 3. Convert saved entities to TemplateInfoSchema (excluding the one we might have added manually)
            for entity in layout_entities:
                # Avoid adding the initial snapshot again if it happens to be saved with the specific ID
                if guild_id and entity.page_identifier == f"guild-designer-{guild_id}":
                    continue
                    
                # Placeholder logic for name - adjust as needed if layouts can be named
                template_name = entity.layout_data.get('name', f"Saved Layout {entity.id}") if isinstance(entity.layout_data, dict) else f"Layout {entity.id}"

                templates_info.append(
                    LayoutTemplateInfoSchema(
                        layout_id=entity.page_identifier,
                        name=template_name,
                        is_shared=False, # Placeholder - Determine if saved layouts can be shared
                        is_initial=False, # User-saved layouts are not the 'initial' one
                        updated_at=entity.updated_at
                    )
                )
            logger.debug(f"Found {len(layout_entities)} potential user-saved templates for user {user_id}")
            return LayoutTemplateListResponse(templates=templates_info)
        except Exception as e:
            logger.error(f"Failed to list user-saved templates for user {user_id}: {e}", exc_info=True)
            # Still return the initial snapshot if it was added
            return LayoutTemplateListResponse(templates=templates_info)

    async def delete_layout(self, user_id: int, page_identifier: str) -> bool:
        """
        Deletes the layout data for a specific user and page.

        Args:
            user_id: The ID of the user.
            page_identifier: The unique identifier for the page.

        Returns:
            True if deletion was successful, False otherwise.
        """
        logger.debug(f"Attempting to delete layout for user {user_id}, page {page_identifier}")
        try:
            success = await self.layout_repository.delete_layout(user_id, page_identifier)
            if success:
                logger.info(f"Successfully deleted layout for user {user_id}, page {page_identifier}")
            else:
                # This might indicate the layout didn't exist, which isn't necessarily an error for deletion
                logger.info(f"Layout for user {user_id}, page {page_identifier} not found or already deleted.")
            return success # Return the repository result
        except Exception as e:
            logger.error(f"Failed to delete layout for user {user_id}, page {page_identifier}: {e}", exc_info=True)
            return False
