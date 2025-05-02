from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.interface.logging.api import get_web_logger
# Correct the service import
from app.web.application.services.template import DashboardConfigurationService
# Import the correct schema names directly
from app.web.interfaces.api.rest.v1.schemas.template_dashboard_schemas import (
    DashboardConfigCreatePayload,
    DashboardConfigUpdatePayload,
    DashboardConfigResponseSchema
)
# Import the DB session dependency
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_web_db_session
# TODO: Import auth dependencies if needed later
# from app.shared.infrastructure.models.auth import AppUserEntity
# from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

logger = get_web_logger()

# --- Dependency for the Service ---
# Rename dependency function and update service it points to
def get_dashboard_configuration_service(
    session: AsyncSession = Depends(get_web_db_session)
) -> DashboardConfigurationService: # Update return type hint
    # This should return the service responsible for Dashboard Configurations
    return DashboardConfigurationService(session)
# ---------------------------------

# Rename the class to better reflect its purpose
class DashboardConfigurationsController(BaseController):
    """Controller for managing dashboard configurations."""

    def __init__(self):
        # Changed prefix to /dashboards/configurations based on route structure
        super().__init__(prefix="/dashboards/configurations", tags=["Guild Designer - Dashboard Configurations"])
        self._register_routes()

    def _register_routes(self):
        """Register API routes for dashboard configurations."""

        # --- Routes for Dashboard Configurations ---
        # Adjust paths relative to the new prefix
        self.router.post(
            "/",
            response_model=DashboardConfigResponseSchema, # TODO: Verify/Update Schema
            status_code=status.HTTP_201_CREATED,
            summary="Create a new Dashboard Configuration"
        )(self.create_dashboard_configuration)

        self.router.get(
            "/",
            response_model=List[DashboardConfigResponseSchema], # TODO: Verify/Update Schema
            summary="List all Dashboard Configurations"
        )(self.list_dashboard_configurations)

        self.router.get(
            "/{config_id}",
            response_model=DashboardConfigResponseSchema, # TODO: Verify/Update Schema
            summary="Get Dashboard Configuration Details"
        )(self.get_dashboard_configuration)

        self.router.put(
            "/{config_id}",
            response_model=DashboardConfigResponseSchema, # TODO: Verify/Update Schema
            summary="Update Dashboard Configuration"
        )(self.update_dashboard_configuration)

        self.router.delete(
            "/{config_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete Dashboard Configuration"
        )(self.delete_dashboard_configuration)

    # --- Endpoint Implementations ---

    async def create_dashboard_configuration(
        self,
        payload: DashboardConfigCreatePayload, # TODO: Verify/Update Schema
        service: DashboardConfigurationService = Depends(get_dashboard_configuration_service) # Update Service Type
        # current_user: AppUserEntity = Depends(get_current_user) # Optional auth
    ) -> DashboardConfigResponseSchema: # TODO: Verify/Update Schema
        logger.info(f"Controller: Request received to create dashboard configuration with payload: {payload}")
        try:
            # Call the correct service method
            new_config = await service.create_configuration(payload)
            return new_config
            # raise NotImplementedError("Service method create_configuration not implemented yet.")
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Controller Error: Unexpected error creating dashboard configuration: {e}", exc_info=True)
            return self.handle_exception(e)

    async def list_dashboard_configurations(
        self,
        service: DashboardConfigurationService = Depends(get_dashboard_configuration_service) # Update Service Type
        # current_user: AppUserEntity = Depends(get_current_user) # Optional auth
    ) -> List[DashboardConfigResponseSchema]: # TODO: Verify/Update Schema
        logger.info(f"Controller: Request received to list dashboard configurations")
        try:
            # Call the correct service method
            configs = await service.list_configurations()
            return configs
            # raise NotImplementedError("Service method list_configurations not implemented yet.")
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Controller Error: Unexpected error listing dashboard configurations: {e}", exc_info=True)
            return self.handle_exception(e)

    async def get_dashboard_configuration(
        self,
        config_id: int,
        service: DashboardConfigurationService = Depends(get_dashboard_configuration_service) # Update Service Type
        # current_user: AppUserEntity = Depends(get_current_user) # Optional auth
    ) -> DashboardConfigResponseSchema: # TODO: Verify/Update Schema
        logger.info(f"Controller: Request received to get dashboard configuration ID: {config_id}")
        try:
            # Call the correct service method
            config = await service.get_configuration(config_id)
            if config is None:
                logger.warning(f"Controller: Dashboard configuration ID {config_id} not found.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard configuration not found")
            return config
            # raise NotImplementedError("Service method get_configuration not implemented yet.")
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Controller Error: Unexpected error getting configuration {config_id}: {e}", exc_info=True)
            return self.handle_exception(e)

    async def update_dashboard_configuration(
        self,
        config_id: int,
        payload: DashboardConfigUpdatePayload, # TODO: Verify/Update Schema
        service: DashboardConfigurationService = Depends(get_dashboard_configuration_service) # Update Service Type
        # current_user: AppUserEntity = Depends(get_current_user) # Optional auth
    ) -> DashboardConfigResponseSchema: # TODO: Verify/Update Schema
        logger.info(f"Controller: Request received to update dashboard configuration ID: {config_id}")
        try:
            # Call the correct service method
            updated_config = await service.update_configuration(config_id, payload)
            if updated_config is None:
                logger.warning(f"Controller: Dashboard configuration ID {config_id} not found for update.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard configuration not found")
            return updated_config
            # raise NotImplementedError("Service method update_configuration not implemented yet.")
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Controller Error: Unexpected error updating configuration {config_id}: {e}", exc_info=True)
            return self.handle_exception(e)

    async def delete_dashboard_configuration(
        self,
        config_id: int,
        service: DashboardConfigurationService = Depends(get_dashboard_configuration_service) # Update Service Type
        # current_user: AppUserEntity = Depends(get_current_user) # Optional auth
    ):
        logger.info(f"Controller: Request received to delete dashboard configuration ID: {config_id}")
        try:
            # Call the correct service method
            deleted = await service.delete_configuration(config_id)
            if not deleted:
                logger.warning(f"Controller: Dashboard configuration ID {config_id} not found for deletion.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard configuration not found")
            return None # Return None with status 204 handled by FastAPI
            # raise NotImplementedError("Service method delete_configuration not implemented yet.")
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Controller Error: Unexpected error deleting configuration {config_id}: {e}", exc_info=True)
            return self.handle_exception(e)

# Instantiate the controller for registration
# Rename variable to match class name
dashboard_configurations_controller = DashboardConfigurationsController() 