from typing import Optional, Dict, Any, List
import logging
from datetime import datetime # Import needed for list_templates

from app.shared.domain.repositories.ui.ui_layout_repository import UILayoutRepository
# Import the new shared repository interface
from app.shared.domain.repositories.ui.shared_ui_layout_template_repository import SharedUILayoutTemplateRepository

from app.shared.infrastructure.models.ui.ui_layout_entity import UILayoutEntity # For type hinting
# Import the shared template entity as well
from app.shared.infrastructure.models.ui import SharedUILayoutTemplateEntity

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
    Handles both user-specific layouts and shared templates.
    """

    def __init__(
        self, 
        layout_repository: UILayoutRepository, 
        shared_layout_repository: SharedUILayoutTemplateRepository # Add shared repo
    ):
        self.layout_repository = layout_repository
        self.shared_layout_repository = shared_layout_repository # Store shared repo

    async def get_layout(self, user_id: int, page_identifier: str) -> Optional[UILayoutResponseSchema]:
        """
        Retrieves the layout data for a specific user and page, formatted for API response.
        (Needs update to handle loading initial snapshot or potentially shared templates by ID)
        """
        # --- TODO: Add logic to handle initial snapshot identifier --- 
        # if page_identifier.startswith("guild-designer-"):
        #     # Construct and return the initial snapshot layout dynamically
        #     # This requires fetching guild structure (channels, categories)
        #     # and converting it into GridstackItem format.
        #     pass 
        
        logger.debug(f"Attempting to get saved layout for user {user_id}, page {page_identifier}")
        layout_entity = await self.layout_repository.get_layout(user_id, page_identifier)
        if layout_entity and isinstance(layout_entity.layout_data, dict):
            logger.debug(f"Layout found for user {user_id}, page {page_identifier}. Formatting response.")
            try:
                grid_items_data = layout_entity.layout_data.get('layout', [])
                is_locked = layout_entity.layout_data.get('is_locked', False)
                parsed_items = [GridstackItem(**item) for item in grid_items_data]
                return UILayoutResponseSchema(
                    page_identifier=layout_entity.page_identifier,
                    layout=parsed_items,
                    is_locked=is_locked,
                    name=layout_entity.layout_data.get('name'),
                    updated_at=layout_entity.updated_at
                )
            except Exception as e:
                logger.error(f"Error processing layout data for user {user_id}, page {page_identifier}: {e}", exc_info=True)
                return None
        else:
            logger.debug(f"No saved layout found or layout_data is not a dict for user {user_id}, page {page_identifier}")
            # --- TODO: Potentially check shared templates by ID/Name here if applicable --- 
            return None

    async def save_layout(self, user_id: int, page_identifier: str, data: UILayoutSaveSchema) -> bool:
        """
        Saves or updates the layout data for a specific user and page.
        """
        layout_data_to_save = {
            "layout": [item.model_dump() for item in data.layout],
            "is_locked": data.is_locked,
            # "name": data.name # If name is part of the save schema later
        }
        logger.debug(f"Saving layout for user {user_id}, page {page_identifier}, lock status: {data.is_locked}")
        try:
            saved_entity = await self.layout_repository.save_layout(
                user_id=user_id,
                page_identifier=page_identifier,
                layout_data=layout_data_to_save
            )
            return bool(saved_entity)
        except Exception as e:
             logger.error(f"Failed to save layout for user {user_id}, page {page_identifier}: {e}", exc_info=True)
             return False

    async def list_templates(self, user_id: int, guild_id: Optional[str] = None, scope: Optional[str] = None) -> LayoutTemplateListResponse:
        """
        Lists available layout templates: initial snapshot, user-saved, and shared.
        """
        logger.debug(f"Listing templates for user {user_id}, guild_id={guild_id}, scope={scope}")
        templates_info: List[LayoutTemplateInfoSchema] = []
        processed_ids = set() # To avoid duplicates if a shared template ID matches a user-specific one

        # 1. Add the Initial Snapshot representation
        if guild_id:
            initial_snapshot_name = f"Initial Snapshot (Guild: {guild_id})"
            initial_snapshot_id = f"guild-designer-{guild_id}"
            if initial_snapshot_id not in processed_ids:
                templates_info.append(LayoutTemplateInfoSchema(
                    layout_id=initial_snapshot_id,
                    name=initial_snapshot_name,
                    is_shared=False,
                    is_initial=True,
                    updated_at=datetime.utcnow() # Placeholder
                ))
                processed_ids.add(initial_snapshot_id)
                logger.debug(f"Added initial snapshot representation for guild {guild_id}")

        # 2. Fetch and add Shared Templates
        try:
            shared_entities = await self.shared_layout_repository.get_all()
            for entity in shared_entities:
                if entity.id not in processed_ids: # Use internal ID if layout_id isn't stored or unique
                    # Assuming shared templates use their DB ID or a specific naming convention for layout_id?
                    # For now, let's use the unique name as the identifier for the list
                    layout_id_for_list = entity.name # Or maybe entity.id needs conversion?
                    templates_info.append(
                        LayoutTemplateInfoSchema(
                            layout_id=layout_id_for_list, # Use unique name for selection
                            name=entity.name,
                            is_shared=True, # Mark as shared
                            is_initial=False,
                            updated_at=entity.updated_at
                        )
                    )
                    processed_ids.add(layout_id_for_list)
            logger.debug(f"Added {len(shared_entities)} shared templates.")
        except Exception as e:
            logger.error(f"Failed to list shared templates: {e}", exc_info=True)
            # Continue without shared templates if error occurs

        # 3. Fetch and add User-Saved Templates
        try:
            # TODO: Filtering by guild_id/scope in the repository
            user_layout_entities = await self.layout_repository.list_layouts(user_id, guild_id, scope)
            for entity in user_layout_entities:
                # Check if this ID was already added (e.g., initial snapshot or shared)
                if entity.page_identifier not in processed_ids:
                    template_name = entity.layout_data.get('name', f"My Layout ({entity.page_identifier})") if isinstance(entity.layout_data, dict) else f"Layout {entity.page_identifier}"
                    templates_info.append(
                        LayoutTemplateInfoSchema(
                            layout_id=entity.page_identifier,
                            name=template_name,
                            is_shared=False,
                            is_initial=False,
                            updated_at=entity.updated_at
                        )
                    )
                    processed_ids.add(entity.page_identifier)
            logger.debug(f"Added {len(user_layout_entities)} potential user-saved templates for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to list user-saved templates for user {user_id}: {e}", exc_info=True)
            # Continue without user templates if error occurs

        return LayoutTemplateListResponse(templates=templates_info)

    async def delete_layout(self, user_id: int, page_identifier: str) -> bool:
        """
        Deletes the layout data for a specific user and page.
        """
        # --- TODO: Should this also delete shared templates if the identifier matches? --- 
        # Currently only deletes from user-specific layouts.
        logger.debug(f"Attempting to delete user layout for user {user_id}, page {page_identifier}")
        try:
            success = await self.layout_repository.delete_layout(user_id, page_identifier)
            if success:
                logger.info(f"Successfully deleted user layout for user {user_id}, page {page_identifier}")
            # No need to log if not found, repo handles that
            return success
        except Exception as e:
            logger.error(f"Failed to delete layout for user {user_id}, page {page_identifier}: {e}", exc_info=True)
            return False

    async def share_layout(
        self, 
        user_id: int, 
        identifier_to_share: str, 
        template_name: str, 
        template_description: Optional[str]
    ) -> bool:
        """
        Shares an existing layout (either initial snapshot or user-saved) 
        as a named, shared template.

        Args:
            user_id: The ID of the user initiating the share.
            identifier_to_share: The page_identifier of the layout to share 
                                 (e.g., 'guild-designer-GUILDID' or a user-specific ID).
            template_name: The name to give the shared template.
            template_description: An optional description for the shared template.

        Returns:
            True if sharing was successful, False otherwise.
        """
        logger.info(f"User {user_id} attempting to share layout '{identifier_to_share}' as template '{template_name}'")
        layout_data_to_share: Optional[Dict[str, Any]] = None

        # 1. Determine the layout data to share
        if identifier_to_share.startswith("guild-designer-"):
            # --- TODO: Implement dynamic generation of Initial Snapshot layout --- 
            logger.warning(f"Dynamic generation of initial snapshot layout for sharing is not yet implemented. Identifier: {identifier_to_share}")
            # For now, let's create a placeholder layout data
            layout_data_to_share = {
                "layout": [
                    {"id": "placeholder-widget-1", "x": 0, "y": 0, "w": 4, "h": 2, "content": "Initial Snapshot (Not Implemented)"}
                ],
                "is_locked": False, # Default lock status for shared template
                "name": f"Initial Snapshot ({identifier_to_share})" # Store original identifier maybe?
            }
            # --- End Placeholder --- 
        else:
            # Load a user-saved layout
            logger.debug(f"Loading user-saved layout '{identifier_to_share}' for user {user_id} to share.")
            saved_layout_entity = await self.layout_repository.get_layout(user_id, identifier_to_share)
            if saved_layout_entity and isinstance(saved_layout_entity.layout_data, dict):
                layout_data_to_share = saved_layout_entity.layout_data
                # Optional: Store the original identifier or name within the shared data?
                # layout_data_to_share['original_identifier'] = identifier_to_share
            else:
                logger.error(f"Could not find user-saved layout '{identifier_to_share}' for user {user_id} to share.")
                return False # Layout to share not found

        # 2. Save the determined layout data as a shared template
        if layout_data_to_share:
            try:
                created_shared_template = await self.shared_layout_repository.create(
                    name=template_name,
                    description=template_description,
                    layout_data=layout_data_to_share,
                    creator_user_id=user_id
                )
                if created_shared_template:
                    logger.info(f"Successfully shared layout '{identifier_to_share}' as template '{template_name}' (ID: {created_shared_template.id}) by user {user_id}")
                    return True
                else:
                    # This could happen if the name was already taken (IntegrityError handled in repo)
                    logger.error(f"Failed to create shared template '{template_name}' in repository (maybe name exists?).")
                    return False
            except Exception as e:
                logger.error(f"Error saving shared template '{template_name}': {e}", exc_info=True)
                return False
        else:
            # This case should ideally be caught earlier (e.g., initial snapshot not implemented)
            logger.error("Layout data to share could not be determined.")
            return False
