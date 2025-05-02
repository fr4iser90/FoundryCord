from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.interface.logging.api import get_web_logger
# Import the service
from app.web.application.services.template import TemplateDashboardInstanceService
# Import the schemas
from app.web.interfaces.api.rest.v1.schemas.template_dashboard_schemas import (
    DashboardInstanceCreatePayload,
    DashboardInstanceUpdatePayload,
    DashboardInstanceResponseSchema
)
# Import the DB session dependency
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_web_db_session
# TODO: Import auth dependencies if needed later
# from app.shared.infrastructure.models.auth import AppUserEntity
# from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

logger = get_web_logger()

# --- Dependency for the Service --- 
def get_template_dashboard_instance_service(
    session: AsyncSession = Depends(get_web_db_session)
) -> TemplateDashboardInstanceService:
    return TemplateDashboardInstanceService(session)
# ---------------------------------

class TemplateDashboardInstancesController(BaseController):
    """Controller for managing dashboard instances linked to guild template channels."""

    def __init__(self):
        # Prefix includes template context, as these instances BELONG to a template channel
        super().__init__(prefix="/templates", tags=["Guild Designer - Dashboard Instances"])
        self._register_routes()

    def _register_routes(self):
        """Register API routes for template-linked dashboard instances."""
        
        # --- Routes relative to Channel Templates ---
        self.router.get(
            "/channels/{channel_template_id}/dashboards",
            response_model=List[DashboardInstanceResponseSchema], # Set response model
            summary="List Dashboard Instances for a Template Channel"
        )(self.list_dashboard_instances_for_channel)

        self.router.post(
            "/channels/{channel_template_id}/dashboards",
            response_model=DashboardInstanceResponseSchema, # Set response model
            status_code=status.HTTP_201_CREATED,
            summary="Create Dashboard Instance for a Template Channel"
        )(self.create_dashboard_instance_for_channel)

        # --- Routes relative to specific Dashboard Instances ---
        self.router.get(
            "/dashboards/{instance_id}",
            response_model=DashboardInstanceResponseSchema, # Set response model
            summary="Get Dashboard Instance Details"
        )(self.get_dashboard_instance)

        self.router.put(
            "/dashboards/{instance_id}",
            response_model=DashboardInstanceResponseSchema, # Set response model
            summary="Update Dashboard Instance"
        )(self.update_dashboard_instance)

        self.router.delete(
            "/dashboards/{instance_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete Dashboard Instance"
        )(self.delete_dashboard_instance)

    # --- Endpoint Implementations ---

    async def list_dashboard_instances_for_channel(
        self,
        channel_template_id: int,
        service: TemplateDashboardInstanceService = Depends(get_template_dashboard_instance_service)
        # current_user: AppUserEntity = Depends(get_current_user) # Optional auth
    ) -> List[DashboardInstanceResponseSchema]:
        logger.info(f"Controller: Request received to list dashboards for channel template ID: {channel_template_id}")
        try:
            instances = await service.list_instances_for_channel(channel_template_id)
            return instances
        except HTTPException as e:
            # Re-raise service-level HTTP exceptions
            raise e 
        except Exception as e:
            logger.error(f"Controller Error: Unexpected error listing instances for channel {channel_template_id}: {e}", exc_info=True)
            # Use base controller's exception handling or raise generic 500
            return self.handle_exception(e) 

    async def create_dashboard_instance_for_channel(
        self,
        channel_template_id: int,
        payload: DashboardInstanceCreatePayload, # Add payload
        service: TemplateDashboardInstanceService = Depends(get_template_dashboard_instance_service)
        # current_user: AppUserEntity = Depends(get_current_user) # Optional auth
    ) -> DashboardInstanceResponseSchema:
        logger.info(f"Controller: Request received to create dashboard for channel template ID: {channel_template_id}")
        try:
            new_instance = await service.create_instance_for_channel(channel_template_id, payload)
            return new_instance
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Controller Error: Unexpected error creating instance for channel {channel_template_id}: {e}", exc_info=True)
            return self.handle_exception(e)

    async def get_dashboard_instance(
        self,
        instance_id: int,
        service: TemplateDashboardInstanceService = Depends(get_template_dashboard_instance_service)
        # current_user: AppUserEntity = Depends(get_current_user) # Optional auth
    ) -> DashboardInstanceResponseSchema:
        logger.info(f"Controller: Request received to get dashboard instance ID: {instance_id}")
        try:
            instance = await service.get_instance(instance_id)
            if instance is None:
                logger.warning(f"Controller: Dashboard instance ID {instance_id} not found.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard instance not found")
            return instance
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Controller Error: Unexpected error getting instance {instance_id}: {e}", exc_info=True)
            return self.handle_exception(e)

    async def update_dashboard_instance(
        self,
        instance_id: int,
        payload: DashboardInstanceUpdatePayload, # Add payload
        service: TemplateDashboardInstanceService = Depends(get_template_dashboard_instance_service)
        # current_user: AppUserEntity = Depends(get_current_user) # Optional auth
    ) -> DashboardInstanceResponseSchema:
        logger.info(f"Controller: Request received to update dashboard instance ID: {instance_id}")
        try:
            updated_instance = await service.update_instance(instance_id, payload)
            if updated_instance is None:
                logger.warning(f"Controller: Dashboard instance ID {instance_id} not found for update.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard instance not found")
            return updated_instance
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Controller Error: Unexpected error updating instance {instance_id}: {e}", exc_info=True)
            return self.handle_exception(e)

    async def delete_dashboard_instance(
        self,
        instance_id: int,
        service: TemplateDashboardInstanceService = Depends(get_template_dashboard_instance_service)
        # current_user: AppUserEntity = Depends(get_current_user) # Optional auth
    ):
        logger.info(f"Controller: Request received to delete dashboard instance ID: {instance_id}")
        try:
            deleted = await service.delete_instance(instance_id)
            if not deleted:
                logger.warning(f"Controller: Dashboard instance ID {instance_id} not found for deletion.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard instance not found")
            # Return None with status 204 handled by FastAPI
            return None 
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Controller Error: Unexpected error deleting instance {instance_id}: {e}", exc_info=True)
            return self.handle_exception(e)

# Instantiate the controller for registration
template_dashboard_instances_controller = TemplateDashboardInstancesController() 