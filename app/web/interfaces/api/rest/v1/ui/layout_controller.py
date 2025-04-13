from fastapi import Depends, HTTPException, status, Body, Request
from typing import Optional, List, Annotated
import logging

# Correct BaseController import
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.web.application.services.ui.layout_service import LayoutService
# Import required schemas, including for the new templates endpoint
from app.web.interfaces.api.rest.v1.schemas.ui_layout_schemas import (
    UILayoutSaveSchema, 
    UILayoutResponseSchema,
    LayoutTemplateListResponse,
    LayoutTemplateInfoSchema
)
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user 
from app.shared.infrastructure.models.auth import AppUserEntity 
# Import the dependency function
from app.web.interfaces.api.rest.dependencies.ui_dependencies import get_layout_service

logger = logging.getLogger(__name__)

class LayoutController(BaseController):
    """Controller for managing UI Layouts via API."""

    def __init__(self):
        super().__init__(prefix="/layouts", tags=["UI Layouts"])
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
            response_model=Optional[UILayoutResponseSchema],
            summary="Get Layout"
        )(self.get_layout)
        
        self.router.post(
            "/{page_identifier}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Save Layout"
        )(self.save_layout)
        
        self.router.delete(
            "/{page_identifier}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete Layout"
        )(self.delete_layout)

    # --- Endpoint Implementations ---

    async def list_templates(
        self,
        layout_service: Annotated[LayoutService, Depends(get_layout_service)],
        current_user: AppUserEntity = Depends(get_current_user),
        guild_id: Optional[str] = None,
        scope: Optional[str] = None
    ) -> LayoutTemplateListResponse:
        """API endpoint to list available layout templates."""
        self.logger.info(f"GET /layouts/templates requested by user {current_user.id}, guild_id={guild_id}, scope={scope}")
        try:
            templates_response = await layout_service.list_templates(
                user_id=current_user.id, 
                guild_id=guild_id, 
                scope=scope
            )
            self.logger.info(f"Found {len(templates_response.templates)} templates for user {current_user.id}")
            return templates_response
        except Exception as e:
            self.logger.error(f"Error listing templates for user {current_user.id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list layout templates.")

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
                self.logger.info(f"No layout found for user {current_user.id}, page {page_identifier}")
                return None 
            
            self.logger.info(f"Successfully retrieved layout {page_identifier} for user {current_user.id}")
            return layout_response
        except Exception as e:
            self.logger.error(f"Error getting layout {page_identifier} for user {current_user.id}: {e}", exc_info=True)
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
            return None
        except Exception as e:
             self.logger.error(f"Error saving layout {page_identifier} for user {current_user.id}: {e}", exc_info=True)
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
            success = await layout_service.delete_layout(current_user.id, page_identifier)
            if not success:
                self.logger.error(f"Service failed to delete layout {page_identifier} for user {current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete layout."
                )
            return None
        except Exception as e:
            self.logger.error(f"Error deleting layout {page_identifier} for user {current_user.id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete layout.")

# Instantiate the controller
layout_controller = LayoutController()
