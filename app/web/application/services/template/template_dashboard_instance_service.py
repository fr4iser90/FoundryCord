from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status # Added for exception handling

from app.shared.interface.logging.api import get_web_logger
# Import the specific repository implementation
from app.shared.domain.repositories.templates.template_dashboard_instance_repository import TemplateDashboardInstanceRepository
# Correct the import path for the repository implementation
from app.shared.infrastructure.repositories.guild_templates import TemplateDashboardInstanceRepositoryImpl
# TODO: Import necessary repositories (e.g., DashboardRepository)
# TODO: Import necessary schemas/models (e.g., DashboardInstanceEntity, DashboardInstanceResponseSchema)
from app.web.interfaces.api.rest.v1.schemas.template_dashboard_schemas import (
    DashboardInstanceCreatePayload,
    DashboardInstanceUpdatePayload,
    DashboardInstanceResponseSchema
)
from app.shared.infrastructure.models.guild_templates import TemplateDashboardInstanceEntity

logger = get_web_logger()

class TemplateDashboardInstanceService:
    """Service layer for managing dashboard instances linked to template channels."""

    def __init__(self, session: AsyncSession):
        self.session = session
        # Instantiate the correct repository
        self.instance_repo = TemplateDashboardInstanceRepositoryImpl(session)

    async def list_instances_for_channel(self, channel_template_id: int) -> List[DashboardInstanceResponseSchema]:
        """Lists all dashboard instances linked to a specific channel template ID."""
        logger.info(f"Service: Listing dashboard instances for channel template ID: {channel_template_id}")
        try:
            instances = await self.instance_repo.get_by_template_channel_id(channel_template_id)
            # Map entities to response schemas
            return [DashboardInstanceResponseSchema.from_orm(inst) for inst in instances]
        except Exception as e:
            logger.error(f"Service Error: Failed to list instances for channel template {channel_template_id}: {e}", exc_info=True)
            # Consider raising a custom service exception or re-raising
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve dashboard instances.")

    async def create_instance_for_channel(
        self,
        channel_template_id: int,
        payload: DashboardInstanceCreatePayload
    ) -> DashboardInstanceResponseSchema:
        """Creates a new dashboard instance and links it to the channel template."""
        logger.info(f"Service: Creating dashboard instance for channel template ID: {channel_template_id} with payload: {payload.dict()}")
        try:
            new_instance = await self.instance_repo.create_for_template(
                guild_template_channel_id=channel_template_id,
                name=payload.name,
                dashboard_type=payload.dashboard_type,
                config=payload.config
            )
            await self.session.commit() 
            await self.session.refresh(new_instance)
            return DashboardInstanceResponseSchema.from_orm(new_instance)
        except Exception as e:
            logger.error(f"Service Error: Failed to create instance for channel template {channel_template_id}: {e}", exc_info=True)
            await self.session.rollback() # Rollback on error
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create dashboard instance.")

    async def get_instance(self, instance_id: int) -> Optional[DashboardInstanceResponseSchema]:
        """Gets the details of a specific dashboard instance by its ID."""
        logger.info(f"Service: Getting dashboard instance ID: {instance_id}")
        try:
            instance = await self.instance_repo.get_by_id(instance_id)
            if not instance:
                logger.warning(f"Service: Dashboard instance ID {instance_id} not found.")
                # Return None here, let controller handle 404
                return None 
            return DashboardInstanceResponseSchema.from_orm(instance)
        except Exception as e:
            logger.error(f"Service Error: Failed to get instance {instance_id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve dashboard instance.")

    async def update_instance(
        self,
        instance_id: int,
        payload: DashboardInstanceUpdatePayload
    ) -> Optional[DashboardInstanceResponseSchema]:
        """Updates an existing dashboard instance."""
        logger.info(f"Service: Updating dashboard instance ID: {instance_id} with payload: {payload.dict(exclude_unset=True)}")
        update_data = payload.dict(exclude_unset=True)
        if not update_data:
            logger.warning(f"Service: No update data provided for instance {instance_id}")
            # Optionally return the existing instance or raise a 400 Bad Request
            instance = await self.instance_repo.get_by_id(instance_id)
            return DashboardInstanceResponseSchema.from_orm(instance) if instance else None

        try:
            updated_instance = await self.instance_repo.update(instance_id, update_data)
            if not updated_instance:
                logger.warning(f"Service: Dashboard instance ID {instance_id} not found for update.")
                return None
            await self.session.commit()
            await self.session.refresh(updated_instance)
            return DashboardInstanceResponseSchema.from_orm(updated_instance)
        except Exception as e:
            logger.error(f"Service Error: Failed to update instance {instance_id}: {e}", exc_info=True)
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update dashboard instance.")

    async def delete_instance(self, instance_id: int) -> bool:
        """Deletes a dashboard instance. Returns True if successful, raises 404 if not found."""
        logger.info(f"Service: Deleting dashboard instance ID: {instance_id}")
        try:
            deleted = await self.instance_repo.delete(instance_id)
            if not deleted:
                logger.warning(f"Service: Dashboard instance ID {instance_id} not found for deletion.")
                return False # Let controller handle 404 based on this
            await self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Service Error: Failed to delete instance {instance_id}: {e}", exc_info=True)
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete dashboard instance.") 