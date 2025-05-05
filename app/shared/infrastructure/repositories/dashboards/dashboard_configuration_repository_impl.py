from typing import Optional, List, Dict, Any
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.interfaces.logging.api import get_web_logger
from app.shared.domain.repositories.dashboards.dashboard_configuration_repository import DashboardConfigurationRepository
from app.shared.infrastructure.models import DashboardConfigurationEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl 

logger = get_web_logger()

class DashboardConfigurationRepositoryImpl(BaseRepositoryImpl[DashboardConfigurationEntity], DashboardConfigurationRepository):
    """SQLAlchemy implementation for the DashboardConfigurationRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(DashboardConfigurationEntity, session)
        logger.debug("DashboardConfigurationRepositoryImpl initialized.")

    async def get_by_id(self, config_id: int) -> Optional[DashboardConfigurationEntity]:
        """Retrieves a dashboard configuration by its unique ID."""
        session_id = id(self.session) # Get ID of the session instance being used
        logger.debug(f"Repository (Session {session_id}): Attempting to get {self.model.__name__} by ID: {config_id}")
        try:
            # Use session.get for primary key lookup
            entity = await self.session.get(self.model, config_id)
            if entity:
                logger.info(f"Repository (Session {session_id}): Found {self.model.__name__} with ID: {config_id}")
            else:
                logger.warning(f"Repository (Session {session_id}): Could not find {self.model.__name__} with ID: {config_id}")
            return entity
        except Exception as e:
            logger.error(f"Repository (Session {session_id}): Error during get_by_id for ID {config_id}: {e}", exc_info=True)
            raise e # Re-raise the exception

    async def list_all(self) -> List[DashboardConfigurationEntity]:
        """Retrieves all dashboard configurations."""
        logger.debug(f"Repository: Getting all dashboard configurations")
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        configs = result.scalars().all()
        logger.debug(f"Repository: Found {len(configs)} dashboard configurations.")
        return configs

    async def find_by_name(self, name: str) -> Optional[DashboardConfigurationEntity]:
        """Retrieves a dashboard configuration by its unique name."""
        logger.debug(f"Repository: Getting dashboard configuration by name: '{name}'")
        stmt = select(self.model).where(self.model.name == name)
        result = await self.session.execute(stmt)
        config = result.scalar_one_or_none()
        if config:
            logger.debug(f"Repository: Found configuration ID: {config.id} for name '{name}'")
        else:
            logger.warning(f"Repository: Could not find configuration with name '{name}'")
        return config

    async def create(
        self,
        name: str,
        dashboard_type: str,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> DashboardConfigurationEntity:
        """Creates a new dashboard configuration."""
        logger.debug(f"Repository: Creating dashboard configuration: name='{name}', type='{dashboard_type}', description='{description}'")
        new_config = DashboardConfigurationEntity(
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

    async def update(self, config_id: int, update_data: Dict[str, Any]) -> Optional[DashboardConfigurationEntity]:
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
