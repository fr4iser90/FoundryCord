from fastapi import APIRouter, HTTPException, status
from typing import List

from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.interface.logging.api import get_web_logger
# from fastapi import Depends
# from app.shared.infrastructure.models.auth import AppUserEntity
# from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

logger = get_web_logger()

class DashboardController(BaseController):
    """Controller for general dashboard-related API endpoints."""

    def __init__(self):
        super().__init__(prefix="/dashboards", tags=["Dashboards (General)"])
        self._register_routes()

    def _register_routes(self):
        """Register API routes for dashboards."""
        self.router.get(
            "/types", 
            response_model=List[str], 
            summary="List Available Dashboard Types"
        )(self.list_available_dashboard_types)

    async def list_available_dashboard_types(
        self,
        # current_user: AppUserEntity = Depends(get_current_user) # Optional: Add auth if needed
    ):
        """Returns a list of all known dashboard type identifiers (strings)."""
        logger.info("Request received to list available dashboard types.")
        try:
            # TODO: Rework dashboard type listing.
            # Need to fetch available types from DB (DashboardTemplate?) or use DashboardCategory Enum
            from app.shared.infrastructure.constants import DashboardCategory # Use Enum instead
            dashboard_types = [category.value for category in DashboardCategory]
            return dashboard_types
        except Exception as e:
            logger.error(f"Error retrieving dashboard types: {e}", exc_info=True)
            return self.handle_exception(e)

dashboard_controller = DashboardController()