from fastapi import APIRouter, HTTPException, status
from typing import List

from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.interfaces.logging.api import get_web_logger
# Import necessary DB components
from app.shared.infrastructure.database.session.context import session_context
from app.shared.infrastructure.repositories.dashboards.dashboard_component_definition_repository_impl import DashboardComponentDefinitionRepositoryImpl
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
        """Returns a list of all available dashboard type identifiers from the database."""
        logger.info("Request received to list available dashboard types.")
        try:
            # Fetch available types from DB (DashboardComponentDefinitionEntity)
            async with session_context() as session:
                repo = DashboardComponentDefinitionRepositoryImpl(session)
                definitions = await repo.list_all()
                # Extract unique dashboard_type strings
                dashboard_types = sorted(list(set(d.dashboard_type for d in definitions)))
            return dashboard_types
        except Exception as e:
            logger.error(f"Error retrieving dashboard types from DB: {e}", exc_info=True)
            return self.handle_exception(e)

dashboard_controller = DashboardController()