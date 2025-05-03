"""
SQLAlchemy implementation for accessing ActiveDashboardEntity instances.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Assuming domain repository interface exists (adapt if needed)
# from app.shared.domain.repositories.dashboards.active_dashboard_repository import ActiveDashboardRepository
from app.shared.infrastructure.models.dashboards import ActiveDashboardEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

# Placeholder interface until domain is defined
class ActiveDashboardRepository:
    async def get_by_id(self, instance_id: int) -> Optional[ActiveDashboardEntity]: raise NotImplementedError
    async def get_by_channel_id(self, channel_id: str) -> Optional[ActiveDashboardEntity]: raise NotImplementedError
    async def get_active_by_guild(self, guild_id: str) -> List[ActiveDashboardEntity]: raise NotImplementedError
    async def list_all_active(self) -> List[ActiveDashboardEntity]: raise NotImplementedError
    async def create(self, **kwargs) -> ActiveDashboardEntity: raise NotImplementedError
    async def update(self, instance_id: int, update_data: Dict[str, Any]) -> Optional[ActiveDashboardEntity]: raise NotImplementedError
    async def delete(self, instance_id: int) -> bool: raise NotImplementedError
    async def set_message_id(self, instance_id: int, message_id: str) -> bool: raise NotImplementedError
    async def set_active_status(self, instance_id: int, is_active: bool) -> bool: raise NotImplementedError

class ActiveDashboardRepositoryImpl(BaseRepositoryImpl[ActiveDashboardEntity], ActiveDashboardRepository):
    """SQLAlchemy implementation for accessing active dashboard instances."""

    def __init__(self, session: AsyncSession):
        """Initializes the repository with an async session."""
        super().__init__(ActiveDashboardEntity, session)
        logger.debug("ActiveDashboardRepositoryImpl initialized.")

    async def get_by_id(self, instance_id: int) -> Optional[ActiveDashboardEntity]:
        """Retrieves an active dashboard instance by its unique ID."""
        logger.debug(f"Repository: Getting ActiveDashboardEntity by ID: {instance_id}")
        return await self.session.get(self.model, instance_id)

    async def get_by_channel_id(self, channel_id: str) -> Optional[ActiveDashboardEntity]:
        """Retrieves an active dashboard instance by its channel ID."""
        logger.debug(f"Repository: Getting ActiveDashboardEntity by channel_id: {channel_id}")
        stmt = select(self.model).where(self.model.channel_id == channel_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_active_by_guild(self, guild_id: str) -> List[ActiveDashboardEntity]:
        """Retrieves all active dashboard instances for a specific guild."""
        logger.debug(f"Repository: Getting active dashboards for guild_id: {guild_id}")
        stmt = select(self.model).where(
            self.model.guild_id == guild_id,
            self.model.is_active == True
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def list_all_active(self) -> List[ActiveDashboardEntity]:
        """Retrieves all active dashboard instances across all guilds, eagerly loading the configuration."""
        logger.debug(f"Repository: Listing all active dashboards with configuration")
        stmt = (
            select(self.model)
            .where(self.model.is_active == True)
            .options(selectinload(self.model.configuration))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, config_id: int, guild_id: str, channel_id: str, message_id: Optional[str] = None, is_active: bool = True, config_override: Optional[Dict[str, Any]] = None) -> ActiveDashboardEntity:
        """Creates a new active dashboard instance."""
        logger.debug(f"Repository: Creating ActiveDashboardEntity for channel_id: {channel_id}")
        new_instance = ActiveDashboardEntity(
            dashboard_configuration_id=config_id,
            guild_id=guild_id,
            channel_id=channel_id,
            message_id=message_id,
            is_active=is_active,
            config_override=config_override
        )
        self.session.add(new_instance)
        await self.session.flush()
        await self.session.refresh(new_instance)
        logger.info(f"Repository: Created ActiveDashboardEntity ID: {new_instance.id} for channel {channel_id}")
        return new_instance

    async def update(self, instance_id: int, update_data: Dict[str, Any]) -> Optional[ActiveDashboardEntity]:
        """Updates an existing active dashboard instance."""
        logger.debug(f"Repository: Updating ActiveDashboardEntity ID: {instance_id} with data: {update_data}")
        instance = await self.get_by_id(instance_id)
        if not instance:
            logger.warning(f"Repository: ActiveDashboardEntity ID {instance_id} not found for update.")
            return None

        for key, value in update_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
            else:
                logger.warning(f"Repository: Attempted to update non-existent attribute '{key}' on instance {instance_id}")

        # Ensure updated_at is automatically handled by DB onupdate trigger
        # instance.updated_at = func.now() # Not needed if onupdate is set
        
        await self.session.flush()
        await self.session.refresh(instance)
        logger.info(f"Repository: Updated ActiveDashboardEntity ID: {instance_id}")
        return instance

    async def delete(self, instance_id: int) -> bool:
        """Deletes an active dashboard instance by its ID."""
        logger.debug(f"Repository: Deleting ActiveDashboardEntity ID: {instance_id}")
        instance = await self.get_by_id(instance_id)
        if not instance:
            logger.warning(f"Repository: ActiveDashboardEntity ID {instance_id} not found for deletion.")
            return False
            
        await self.session.delete(instance)
        await self.session.flush()
        logger.info(f"Repository: Deleted ActiveDashboardEntity ID: {instance_id}")
        return True
        
    async def set_message_id(self, instance_id: int, message_id: Optional[str]) -> bool:
        """Sets or updates the message_id for an active dashboard instance."""
        logger.debug(f"Repository: Setting message_id={message_id} for ActiveDashboardEntity ID: {instance_id}")
        result = await self.session.execute(
            update(self.model)
            .where(self.model.id == instance_id)
            .values(message_id=message_id)
        )
        await self.session.flush()
        if result.rowcount > 0:
            logger.info(f"Repository: Successfully updated message_id for instance {instance_id}")
            return True
        else:
            logger.warning(f"Repository: Failed to update message_id for instance {instance_id} (not found or no change)")
            return False

    async def set_active_status(self, instance_id: int, is_active: bool) -> bool:
        """Sets the active status for a dashboard instance."""
        logger.debug(f"Repository: Setting is_active={is_active} for ActiveDashboardEntity ID: {instance_id}")
        result = await self.session.execute(
            update(self.model)
            .where(self.model.id == instance_id)
            .values(is_active=is_active)
        )
        await self.session.flush()
        if result.rowcount > 0:
            logger.info(f"Repository: Successfully updated is_active status for instance {instance_id}")
            return True
        else:
            logger.warning(f"Repository: Failed to update is_active status for instance {instance_id} (not found or no change)")
            return False 