from typing import Optional, List, Dict, Any
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.interface.logging.api import get_web_logger
from app.shared.domain.repositories.dashboards.dashboard_configuration_repository import DashboardConfigurationRepository
from app.shared.infrastructure.models.guild_templates import TemplateDashboardInstanceEntity
# Assuming BaseRepositoryImpl exists and provides common CRUD operations
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl 

logger = get_web_logger()

class DashboardConfigurationRepositoryImpl(BaseRepositoryImpl[TemplateDashboardInstanceEntity], DashboardConfigurationRepository):
    """SQLAlchemy implementation for the DashboardConfigurationRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(TemplateDashboardInstanceEntity, session)
        logger.debug("DashboardConfigurationRepositoryImpl initialized.")

    async def get_by_id(self, config_id: int) -> Optional[TemplateDashboardInstanceEntity]:
        """Retrieves a dashboard configuration by its unique ID."""
        logger.debug(f"Repository: Getting dashboard configuration by ID: {config_id}")
        return await super().get_by_id(config_id)

    async def list_all(self) -> List[TemplateDashboardInstanceEntity]:
        """Retrieves all dashboard configurations."""
        logger.debug(f"Repository: Getting all dashboard configurations")
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        configs = result.scalars().all()
        logger.debug(f"Repository: Found {len(configs)} dashboard configurations.")
        return configs

    async def create(
        self,
        name: str,
        dashboard_type: str,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> TemplateDashboardInstanceEntity:
        """Creates a new dashboard configuration."""
        logger.debug(f"Repository: Creating dashboard configuration: name='{name}', type='{dashboard_type}', description='{description}'")
        new_config = TemplateDashboardInstanceEntity(
            name=name,
            dashboard_type=dashboard_type,
            description=description,
            config=config
        )
        self.session.add(new_config)
        await self.session.flush()
        await self.session.refresh(new_config)
        logger.info(f"Repository: Created dashboard configuration ID: {new_config.id}")
        return new_config

    async def update(self, config_id: int, update_data: Dict[str, Any]) -> Optional[TemplateDashboardInstanceEntity]:
        """Updates an existing dashboard configuration."""
        logger.debug(f"Repository: Updating dashboard configuration ID: {config_id} with data: {update_data}")
        config_entity = await self.get_by_id(config_id)
        if not config_entity:
            logger.warning(f"Repository: Dashboard configuration ID {config_id} not found for update.")
            return None

        # Update fields
        for key, value in update_data.items():
            if hasattr(config_entity, key):
                setattr(config_entity, key, value)
            else:
                logger.warning(f"Repository: Attempted to update non-existent attribute '{key}' on configuration {config_id}")

        await self.session.flush()
        await self.session.refresh(config_entity)
        logger.info(f"Repository: Updated dashboard configuration ID: {config_id}")
        return config_entity

    async def delete(self, config_id: int) -> bool:
        """Deletes a dashboard configuration by its ID. Returns True if deletion was successful, False otherwise."""
        logger.debug(f"Repository: Deleting dashboard configuration ID: {config_id}")
        config_entity = await self.get_by_id(config_id)
        if not config_entity:
            logger.warning(f"Repository: Dashboard configuration ID {config_id} not found for deletion.")
            return False
        
        await self.session.delete(config_entity)
        await self.session.flush()
        logger.info(f"Repository: Deleted dashboard configuration ID: {config_id}")
        return True
