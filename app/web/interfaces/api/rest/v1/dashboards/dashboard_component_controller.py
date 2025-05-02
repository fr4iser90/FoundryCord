"""
API Controller for retrieving Dashboard Component Definitions.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.interface.logging.api import get_web_logger
# Import the service
from app.web.application.services.dashboards import DashboardComponentService
# Import the response schema
from app.web.interfaces.api.rest.v1.schemas.dashboard_component_schemas import ComponentDefinitionListResponseSchema, ComponentDefinitionSchema
# Import the DB session dependency
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_web_db_session

logger = get_web_logger()

# --- Dependency for the Service --- 
def get_dashboard_component_service(
    session: AsyncSession = Depends(get_web_db_session)
) -> DashboardComponentService:
    return DashboardComponentService(session)
# ---------------------------------

class DashboardComponentController(BaseController):
    """Controller for managing dashboard component definitions."""

    def __init__(self):
        super().__init__(prefix="/dashboards", tags=["Dashboards - Components"])
        self._register_routes()

    def _register_routes(self):
        """Register API routes for dashboard component definitions."""
        
        self.router.get(
            "/components",
            response_model=ComponentDefinitionListResponseSchema,
            summary="List Available Dashboard Component Definitions"
        )(self.list_component_definitions)

    # --- Endpoint Implementations ---

    async def list_component_definitions(
        self,
        dashboard_type: Optional[str] = Query(None, description="Filter by dashboard type (e.g., 'common', 'welcome')"),
        component_type: Optional[str] = Query(None, description="Filter by component type (e.g., 'button', 'embed')"),
        service: DashboardComponentService = Depends(get_dashboard_component_service)
        # Add auth dependency if needed: current_user: AppUserEntity = Depends(get_current_user)
    ) -> ComponentDefinitionListResponseSchema:
        """Retrieve a list of available dashboard component definitions, with optional filters."""
        logger.info(f"Controller: Request received to list dashboard components (dashboard_type={dashboard_type}, component_type={component_type})")
        try:
            definitions: List[ComponentDefinitionSchema] = await service.list_definitions(
                dashboard_type=dashboard_type,
                component_type=component_type
            )
            # Wrap the list in the response schema structure
            return ComponentDefinitionListResponseSchema(components=definitions)
        except HTTPException as e:
            # Re-raise HTTP exceptions from the service layer
            raise e 
        except Exception as e:
            logger.error(f"Controller Error: Unexpected error listing dashboard components: {e}", exc_info=True)
            # Use base controller's exception handling or raise generic 500
            # Assuming BaseController has a handle_exception method
            if hasattr(self, 'handle_exception') and callable(self.handle_exception):
                 return self.handle_exception(e)
            else:
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

# Instantiate the controller for registration
dashboard_component_controller = DashboardComponentController() 