from fastapi import Depends, HTTPException, status, Body, Request
from typing import Optional, List
import logging

# Correct BaseController import
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.web.application.services.ui.layout_service import LayoutService
from app.web.interfaces.api.rest.v1.schemas.ui_layout_schemas import UILayoutSaveSchema, UILayoutResponseSchema
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user 
from app.shared.infrastructure.models.auth import AppUserEntity 
# Import the new dependency function (we will create this next)
# Assuming it will be in a new file ui_dependencies.py
from app.web.interfaces.api.rest.dependencies.ui_dependencies import get_layout_service # Adjust path if needed

logger = logging.getLogger(__name__)

# No need for a separate router instance here, BaseController provides self.router

class LayoutController(BaseController):
    """Controller for managing UI Layouts via API."""

    def __init__(self):
        # No need to get service from factory here
        super().__init__(prefix="/layouts", tags=["UI Layouts"])
        self._register_routes()

    def _register_routes(self):
        """Register API routes for UI layouts."""
        self.router.get(
            "/{page_identifier}",
            response_model=Optional[UILayoutResponseSchema],
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
            summary="Reset User Layout"
        )(self.reset_layout)

    # --- Endpoint Implementations ---
    # Methods now need layout_service passed as an argument 

    async def get_layout(
        self, 
        page_identifier: str,
        current_user: AppUserEntity = Depends(get_current_user),
        layout_service: LayoutService = Depends(get_layout_service)
    ):
        """Endpoint to get the user's saved layout for a page."""
        self.logger.info(f"GET /layouts/{page_identifier} requested by user {current_user.id}")
        try:
            layout_data = await layout_service.get_user_layout(current_user.id, page_identifier)
            if layout_data is None:
                self.logger.info(f"No layout found for user {current_user.id}, page {page_identifier}")
                return None 
            
            return UILayoutResponseSchema(page_identifier=page_identifier, layout=layout_data.get('layout', []))
        except Exception as e:
            return self.handle_exception(e)

    async def save_layout(
        self, 
        page_identifier: str,
        layout_payload: UILayoutSaveSchema,
        current_user: AppUserEntity = Depends(get_current_user),
        layout_service: LayoutService = Depends(get_layout_service)
    ):
        """Endpoint to save/update the user's layout for a page."""
        self.logger.info(f"POST /layouts/{page_identifier} requested by user {current_user.id}")
        try:
            layout_data_to_save = {"layout": [item.dict(exclude_unset=True) for item in layout_payload.layout]}

            success = await layout_service.save_user_layout(
                user_id=current_user.id,
                page_identifier=page_identifier,
                layout_data=layout_data_to_save 
            )
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save layout."
                )
            return None
        except Exception as e:
             return self.handle_exception(e)

    async def reset_layout(
        self, 
        page_identifier: str,
        current_user: AppUserEntity = Depends(get_current_user),
        layout_service: LayoutService = Depends(get_layout_service)
    ):
        """Endpoint to delete/reset the user's layout for a page."""
        self.logger.info(f"DELETE /layouts/{page_identifier} requested by user {current_user.id}")
        try:
            success = await layout_service.reset_user_layout(current_user.id, page_identifier)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to reset layout."
                )
            return None
        except Exception as e:
            return self.handle_exception(e)

# Instantiate the controller
layout_controller = LayoutController()

# We don't need to export a specifically named router from here
# The generic 'router' will be accessed via the instance in __init__.py
# ui_layout_router = layout_controller.router # REMOVE THIS LINE IF IT EXISTS
