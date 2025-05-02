from typing import Optional, List, Dict, Any
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.interface.logging.api import get_web_logger
from app.shared.domain.repositories.templates.template_dashboard_instance_repository import TemplateDashboardInstanceRepository
from app.shared.infrastructure.models.guild_templates import TemplateDashboardInstanceEntity
# Assuming BaseRepositoryImpl exists and provides common CRUD operations
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl 

logger = get_web_logger()

class TemplateDashboardInstanceRepositoryImpl(BaseRepositoryImpl[TemplateDashboardInstanceEntity], TemplateDashboardInstanceRepository):
    """SQLAlchemy implementation for the TemplateDashboardInstanceRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(TemplateDashboardInstanceEntity, session)
        logger.debug("TemplateDashboardInstanceRepositoryImpl initialized.")

    async def get_by_id(self, instance_id: int) -> Optional[TemplateDashboardInstanceEntity]:
        """Retrieves a dashboard instance by its unique ID."""
        logger.debug(f"Repository: Getting template dashboard instance by ID: {instance_id}")
        return await super().get_by_id(instance_id)

    async def get_by_template_channel_id(self, channel_template_id: int) -> List[TemplateDashboardInstanceEntity]:
        """Retrieves all dashboard instances linked to a specific guild template channel ID."""
        logger.debug(f"Repository: Getting template dashboard instances for channel template ID: {channel_template_id}")
        stmt = select(self.model).where(self.model.guild_template_channel_id == channel_template_id)
        result = await self.session.execute(stmt)
        instances = result.scalars().all()
        logger.debug(f"Repository: Found {len(instances)} instances for channel template ID: {channel_template_id}")
        return instances

    async def create_for_template(
        self,
        guild_template_channel_id: int,
        name: str,
        dashboard_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> TemplateDashboardInstanceEntity:
        """Creates a new dashboard instance linked to a template channel."""
        logger.debug(f"Repository: Creating template dashboard instance: name='{name}', type='{dashboard_type}', channel_template_id={guild_template_channel_id}")
        new_instance = TemplateDashboardInstanceEntity(
            guild_template_channel_id=guild_template_channel_id,
            name=name,
            dashboard_type=dashboard_type,
            config=config
        )
        self.session.add(new_instance)
        await self.session.flush()
        await self.session.refresh(new_instance)
        logger.info(f"Repository: Created template dashboard instance ID: {new_instance.id}")
        return new_instance

    async def update(self, instance_id: int, update_data: Dict[str, Any]) -> Optional[TemplateDashboardInstanceEntity]:
        """Updates an existing dashboard instance with the provided data."""
        logger.debug(f"Repository: Updating template dashboard instance ID: {instance_id} with data: {update_data}")
        instance = await self.get_by_id(instance_id)
        if not instance:
            logger.warning(f"Repository: Template dashboard instance ID {instance_id} not found for update.")
            return None

        # Update fields
        for key, value in update_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
            else:
                logger.warning(f"Repository: Attempted to update non-existent attribute '{key}' on instance {instance_id}")

        await self.session.flush()
        await self.session.refresh(instance)
        logger.info(f"Repository: Updated template dashboard instance ID: {instance_id}")
        return instance

    async def delete(self, instance_id: int) -> bool:
        """Deletes a dashboard instance by its ID. Returns True if deletion was successful, False otherwise."""
        logger.debug(f"Repository: Deleting template dashboard instance ID: {instance_id}")
        instance = await self.get_by_id(instance_id)
        if not instance:
            logger.warning(f"Repository: Template dashboard instance ID {instance_id} not found for deletion.")
            return False
        
        await self.session.delete(instance)
        await self.session.flush()
        logger.info(f"Repository: Deleted template dashboard instance ID: {instance_id}")
        return True
