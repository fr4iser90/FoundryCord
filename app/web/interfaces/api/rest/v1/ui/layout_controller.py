from fastapi import Depends, HTTPException, status, Body, Request
from typing import Optional, List, Annotated
import logging

# Correct BaseController import
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.web.application.services.ui.layout_service import LayoutService
# Import required schemas - REMOVED template/sharing schemas
from app.web.interfaces.api.rest.v1.schemas.ui_layout_schemas import (
    UILayoutSaveSchema, 
    UILayoutResponseSchema
    # LayoutTemplateListResponse,
    # LayoutTemplateInfoSchema,
    # LayoutShareRequestSchema
)
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user 
from app.shared.infrastructure.models.auth import AppUserEntity 
# Import the dependency function
from app.web.interfaces.api.rest.dependencies.ui_dependencies import get_layout_service

logger = logging.getLogger(__name__)

class LayoutController(BaseController):
    """Controller for managing user-specific UI Layouts via API."""

    def __init__(self):
        # Corrected prefix to be relative if BaseController adds /api/v1 
        # Assuming BaseController does NOT add /api/v1 automatically for API controllers
        # If it does, prefix should be just "/layouts"
        # Keeping original prefix for now, assuming it's correct relative to v1 router.
        super().__init__(prefix="/layouts", tags=["UI Layouts"]) 
        self._register_routes()

    def _register_routes(self):
        """Register API routes for user-specific UI layouts."""

        # REMOVED list_templates route registration
        # REMOVED share_layout_template route registration
        
        self.router.get(
            "/{page_identifier}",
            response_model=Optional[UILayoutResponseSchema], # Allow None response
            summary="Get User Layout"
        )(self.get_layout)
        
        self.router.post(
            "/{page_identifier}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Save User Layout"
        )(self.save_layout)
        
        self.router.delete(
            "/{page_identifier}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete User Layout (Reset)" # Clarified purpose
        )(self.delete_layout)


    # --- Endpoint Implementations --- 

    # REMOVED list_templates method
    # REMOVED share_layout_template method

    async def get_layout(
        self, 
        page_identifier: str,
        layout_service: Annotated[LayoutService, Depends(get_layout_service)],
        current_user: AppUserEntity = Depends(get_current_user)
    ) -> Optional[UILayoutResponseSchema]:
        """Endpoint to get the user's saved layout for a page."""
        self.logger.info(f"GET /layouts/{page_identifier} requested by user {current_user.id}")
        try:
            layout_response = await layout_service.get_layout(current_user.id, page_identifier)
            if layout_response is None:
                # Correctly return None which FastAPI handles (no 404 needed here)
                self.logger.info(f"No layout found for user {current_user.id}, page {page_identifier}")
                return None 
            
            self.logger.info(f"Successfully retrieved layout {page_identifier} for user {current_user.id}")
            return layout_response
        except Exception as e:
            self.logger.error(f"Error getting layout {page_identifier} for user {current_user.id}: {e}", exc_info=True)
            # Let base exception handler deal with 500
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve layout.")

    async def save_layout(
        self, 
        page_identifier: str,
        layout_payload: UILayoutSaveSchema,
        layout_service: Annotated[LayoutService, Depends(get_layout_service)],
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """Endpoint to save/update the user's layout for a page."""
        self.logger.info(f"POST /layouts/{page_identifier} requested by user {current_user.id}")
        try:
            success = await layout_service.save_layout(
                user_id=current_user.id,
                page_identifier=page_identifier,
                data=layout_payload 
            )
            if not success:
                self.logger.error(f"Service failed to save layout {page_identifier} for user {current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save layout."
                )
            # Return None for 204 No Content status
            return None
        except Exception as e:
             self.logger.error(f"Error saving layout {page_identifier} for user {current_user.id}: {e}", exc_info=True)
             # Let base exception handler deal with 500
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save layout.")

    async def delete_layout(
        self, 
        page_identifier: str,
        layout_service: Annotated[LayoutService, Depends(get_layout_service)],
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """Endpoint to delete/reset the user's layout for a page."""
        self.logger.info(f"DELETE /layouts/{page_identifier} requested by user {current_user.id}")
        try:
            # Service returns True if deleted or didn't exist, False on error
            success = await layout_service.delete_layout(current_user.id, page_identifier)
            if not success:
                # This indicates an actual error during deletion attempt
                self.logger.error(f"Service failed to delete layout {page_identifier} for user {current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete layout."
                )
            # Return None for 204 No Content status
            return None
        except Exception as e:
            self.logger.error(f"Error deleting layout {page_identifier} for user {current_user.id}: {e}", exc_info=True)
            # Let base exception handler deal with 500
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete layout.")

# Instantiate the controller
layout_controller = LayoutController()
