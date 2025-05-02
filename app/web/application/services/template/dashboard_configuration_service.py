from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.shared.interface.logging.api import get_web_logger
# TODO: Rename Repository interface import
from app.shared.domain.repositories.templates.template_dashboard_instance_repository import DashboardConfigurationRepository
# TODO: Rename Repository implementation import
from app.shared.infrastructure.repositories.guild_templates import DashboardConfigurationRepositoryImpl # Corrected import path
# TODO: Rename Schemas import
from app.web.interfaces.api.rest.v1.schemas.template_dashboard_schemas import (
    DashboardConfigCreatePayload,
    DashboardConfigUpdatePayload,
    DashboardConfigResponseSchema
)
# TODO: Rename Entity import
from app.shared.infrastructure.models.guild_templates import TemplateDashboardInstanceEntity

logger = get_web_logger()

# TODO: Rename Service class
class DashboardConfigurationService:
    """Service layer for managing dashboard configurations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        # Instantiate the correct repository
        self.config_repo: DashboardConfigurationRepository = DashboardConfigurationRepositoryImpl(session) # Use updated repo interface/impl

    # REMOVED: list_instances_for_channel method
    # async def list_instances_for_channel(...):

    # REMOVED: create_instance_for_channel method
    # async def create_instance_for_channel(...):
    
    async def list_configurations(self) -> List[DashboardConfigResponseSchema]: # New Method
        """Lists all dashboard configurations."""
        logger.info(f"Service: Listing all dashboard configurations")
        try:
            configs = await self.config_repo.list_all()
            return [DashboardConfigResponseSchema.from_orm(cfg) for cfg in configs]
        except Exception as e:
            logger.error(f"Service Error: Failed to list dashboard configurations: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve dashboard configurations.")

    async def create_configuration(
        self,
        payload: DashboardConfigCreatePayload
    ) -> DashboardConfigResponseSchema: # New Method
        """Creates a new dashboard configuration."""
        logger.info(f"Service: Creating dashboard configuration with payload: {payload.dict()}")
        try:
            new_config = await self.config_repo.create(
                name=payload.name,
                dashboard_type=payload.dashboard_type,
                description=payload.description,
                config=payload.config
            )
            await self.session.commit() 
            await self.session.refresh(new_config)
            return DashboardConfigResponseSchema.from_orm(new_config)
        except Exception as e:
            logger.error(f"Service Error: Failed to create dashboard configuration: {e}", exc_info=True)
            await self.session.rollback() # Rollback on error
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create dashboard configuration.")

    async def get_configuration(self, config_id: int) -> Optional[DashboardConfigResponseSchema]: # Renamed method and param
        """Gets the details of a specific dashboard configuration by its ID."""
        logger.info(f"Service: Getting dashboard configuration ID: {config_id}")
        try:
            config_entity = await self.config_repo.get_by_id(config_id) # Use renamed param
            if not config_entity:
                logger.warning(f"Service: Dashboard configuration ID {config_id} not found.")
                return None 
            return DashboardConfigResponseSchema.from_orm(config_entity)
        except Exception as e:
            logger.error(f"Service Error: Failed to get configuration {config_id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve dashboard configuration.")

    async def update_configuration(
        self,
        config_id: int, # Renamed param
        payload: DashboardConfigUpdatePayload
    ) -> Optional[DashboardConfigResponseSchema]: # Renamed method
        """Updates an existing dashboard configuration."""
        logger.info(f"Service: Updating dashboard configuration ID: {config_id} with payload: {payload.dict(exclude_unset=True)}")
        update_data = payload.dict(exclude_unset=True)
        if not update_data:
            logger.warning(f"Service: No update data provided for configuration {config_id}")
            config_entity = await self.config_repo.get_by_id(config_id)
            return DashboardConfigResponseSchema.from_orm(config_entity) if config_entity else None

        try:
            updated_config = await self.config_repo.update(config_id, update_data) # Use renamed param
            if not updated_config:
                logger.warning(f"Service: Dashboard configuration ID {config_id} not found for update.")
                return None
            await self.session.commit()
            await self.session.refresh(updated_config)
            return DashboardConfigResponseSchema.from_orm(updated_config)
        except Exception as e:
            logger.error(f"Service Error: Failed to update configuration {config_id}: {e}", exc_info=True)
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update dashboard configuration.")

    async def delete_configuration(self, config_id: int) -> bool: # Renamed method and param
        """Deletes a dashboard configuration. Returns True if successful."""
        logger.info(f"Service: Deleting dashboard configuration ID: {config_id}")
        try:
            deleted = await self.config_repo.delete(config_id) # Use renamed param
            if not deleted:
                logger.warning(f"Service: Dashboard configuration ID {config_id} not found for deletion.")
                return False 
            await self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Service Error: Failed to delete configuration {config_id}: {e}", exc_info=True)
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete dashboard configuration.") 