from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Annotated
from datetime import datetime

from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
# Import the layout schemas
from app.web.interfaces.api.rest.v1.schemas.ui_layout_schemas import (
    UILayoutSaveSchema, 
    UILayoutResponseSchema, 
    LayoutTemplateListResponse, 
    LayoutTemplateInfoSchema # Needed if service returns this type
)
# Import the actual LayoutService
from app.web.application.services.ui.layout_service import LayoutService 
# Corrected import path for the dependency provider
from app.web.interfaces.api.rest.dependencies.ui_dependencies import get_layout_service 

class LayoutController(BaseController):
    """Controller for managing UI layouts (Gridstack)."""

    def __init__(self):
        super().__init__(prefix="/layouts", tags=["UI Layouts"])
        # Service is now injected via Depends in each route
        self._register_routes()

    def _register_routes(self):
        """Register API routes for UI layouts."""
        self.router.get(
            "/templates", 
            response_model=LayoutTemplateListResponse,
            summary="List Available Layout Templates",
            description="Retrieves a list of saved layout templates accessible to the user."
        )(self.list_templates)

        self.router.get(
            "/{page_identifier}",
            response_model=Optional[UILayoutResponseSchema], # Optional because it might not exist
            summary="Get Saved Layout",
            description="Retrieves the saved layout state for a specific page identifier."
        )(self.get_layout)

        self.router.post(
            "/{page_identifier}",
            status_code=status.HTTP_204_NO_CONTENT, # Return 204 on successful save
            summary="Save Layout",
            description="Saves the layout state (structure and lock status) for a specific page identifier."
        )(self.save_layout)

        self.router.delete(
            "/{page_identifier}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete Saved Layout",
            description="Deletes the saved layout state for a specific page identifier (resets to default)."
        )(self.delete_layout)

    async def list_templates(
        self,
        layout_service: Annotated[LayoutService, Depends(get_layout_service)], # Inject service
        guild_id: Optional[str] = None,
        scope: Optional[str] = None,
        current_user: AppUserEntity = Depends(get_current_user)
    ) -> LayoutTemplateListResponse:
        """API endpoint to list available layout templates."""
        try:
            self.logger.info(f"Fetching templates for user {current_user.id}, guild_id={guild_id}, scope={scope}")
            # Call the actual service method
            templates_response = await layout_service.list_templates(
                user_id=current_user.id, 
                guild_id=guild_id, 
                scope=scope
            )
            
            self.logger.info(f"Found {len(templates_response.templates)} templates.")
            return templates_response # Return the response from the service

        except Exception as e:
            self.logger.error(f"Error listing templates: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list layout templates.")

    async def get_layout(
        self,
        page_identifier: str,
        layout_service: Annotated[LayoutService, Depends(get_layout_service)], # Inject service
        current_user: AppUserEntity = Depends(get_current_user)
    ) -> Optional[UILayoutResponseSchema]:
        """API endpoint to retrieve a saved layout."""
        try:
            self.logger.info(f"Fetching layout for identifier: {page_identifier} for user {current_user.id}")
            # Call the actual service method
            layout_response = await layout_service.get_layout(
                page_identifier=page_identifier, 
                user_id=current_user.id
            )
            
            if not layout_response:
                self.logger.info(f"Layout {page_identifier} not found for user {current_user.id}.")
                # Return None, FastAPI handles as 404 due to Optional[UILayoutResponseSchema]
                return None 
            
            self.logger.info(f"Successfully retrieved layout {page_identifier} for user {current_user.id}")
            return layout_response # Return the schema directly from the service

        except Exception as e:
            self.logger.error(f"Error getting layout {page_identifier}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve layout.")

    async def save_layout(
        self,
        page_identifier: str,
        payload: UILayoutSaveSchema, 
        layout_service: Annotated[LayoutService, Depends(get_layout_service)], # Inject service
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """API endpoint to save a layout."""
        try:
            self.logger.info(f"Saving layout for identifier: {page_identifier} by user {current_user.id}")
            # Call the actual service method, passing the payload directly
            success = await layout_service.save_layout(
                page_identifier=page_identifier, 
                user_id=current_user.id, 
                data=payload # Pass the whole validated schema
            )
            
            if not success:
                self.logger.error(f"Service failed to save layout {page_identifier} for user {current_user.id}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save layout due to a server error.")

            self.logger.info(f"Layout {page_identifier} saved successfully for user {current_user.id}.")
            # No content returned on success (204)
            return 

        except HTTPException as http_exc:
            # Re-raise validation errors or specific HTTP exceptions
            raise http_exc
        except Exception as e:
            self.logger.error(f"Error saving layout {page_identifier}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save layout.")

    async def delete_layout(
        self,
        page_identifier: str,
        layout_service: Annotated[LayoutService, Depends(get_layout_service)], # Inject service
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """API endpoint to delete/reset a saved layout."""
        try:
            self.logger.info(f"Deleting layout for identifier: {page_identifier} by user {current_user.id}")
            # Call the actual service method
            success = await layout_service.delete_layout(
                page_identifier=page_identifier, 
                user_id=current_user.id
            )

            # The service/repo now returns True even if not found, 
            # only returns False on actual DB error during delete.
            if not success: 
                 self.logger.error(f"Service failed to delete layout {page_identifier} for user {current_user.id}")
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete layout due to a server error.")

            self.logger.info(f"Layout {page_identifier} deleted (or confirmed not present) successfully for user {current_user.id}.")
            # No content returned on success (204)
            return

        except Exception as e:
            self.logger.error(f"Error deleting layout {page_identifier}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete layout.")

# Instantiate the controller - This might need adjustment depending on how FastAPI app is structured
# If using factory pattern or app setup function, instantiation might happen elsewhere.
# For now, assuming this direct instantiation works or is handled appropriately.
layout_controller = LayoutController() 