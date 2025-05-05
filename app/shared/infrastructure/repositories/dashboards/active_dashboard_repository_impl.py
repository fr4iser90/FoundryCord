"""
SQLAlchemy implementation for accessing ActiveDashboardEntity instances.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import null

# Assuming domain repository interface exists (adapt if needed)
# from app.shared.domain.repositories.dashboards.active_dashboard_repository import ActiveDashboardRepository
from app.shared.infrastructure.models.dashboards import ActiveDashboardEntity
from app.shared.infrastructure.repositories.base_repository_impl import BaseRepositoryImpl
from app.shared.interfaces.logging.api import get_db_logger

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
    async def set_message_id(self, instance_id: int, message_id: Optional[str]) -> bool: raise NotImplementedError
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

    async def create(self, dashboard_configuration_id: int, guild_id: str, channel_id: str, message_id: Optional[str] = None, is_active: bool = True) -> ActiveDashboardEntity:
        """Creates a new active dashboard instance."""
        logger.debug(f"Repository: Creating ActiveDashboardEntity for channel_id: {channel_id}")

        # Prepare data dictionary for the entity constructor
        entity_data = {
            "dashboard_configuration_id": dashboard_configuration_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "is_active": is_active
            # message_id is added conditionally below
        }

        # Convert message_id to int if provided
        if message_id is not None:
            try:
                message_id_int = int(message_id)
                # Add message_id to the dictionary ONLY if it's not None and conversion is successful
                entity_data["message_id"] = message_id_int
            except (ValueError, TypeError):
                logger.warning(f"Repository: Invalid message_id '{message_id}' provided during create for channel {channel_id}. Setting message_id to NULL in DB.")
                # Do NOT add the key 'message_id' to entity_data if it's invalid or None
        
        # Create instance using dictionary unpacking.
        # If message_id was None or invalid, the key 'message_id' won't be in entity_data.
        # SQLAlchemy should then rely on the database column's default (NULL).
        new_instance = ActiveDashboardEntity(**entity_data)

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
                # Special handling for message_id: Convert to int or None
                if key == 'message_id':
                    if value is None:
                        setattr(instance, key, None)
                    else:
                        try:
                            setattr(instance, key, int(value))
                        except (ValueError, TypeError):
                            logger.warning(f"Repository Update: Invalid message_id '{value}' for instance {instance_id}. Skipping update for this field.")
                # Add handling for config_override if needed in update later
                # elif key == 'config_override':
                #     # Ensure value is a dict or None
                #     if isinstance(value, dict) or value is None:
                #         setattr(instance, key, value)
                #     else:
                #          logger.warning(f"Repository Update: Invalid config_override type for instance {instance_id}. Skipping update.")
                else:
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

        # Convert to int or use null()
        message_id_value = None
        if message_id is not None:
            try:
                message_id_value = int(message_id)
            except (ValueError, TypeError):
                logger.warning(f"Repository SetMessageID: Invalid message_id '{message_id}' for instance {instance_id}. Setting to NULL.")
                message_id_value = null() # Use null() if invalid
        else:
            message_id_value = null() # Use null() if None

        result = await self.session.execute(
            update(self.model)
            .where(self.model.id == instance_id)
            .values(message_id=message_id_value) # Pass the converted int or null()
        )
        await self.session.flush()
        if result.rowcount > 0:
            logger.debug(f"Repository: Successfully updated message_id for instance {instance_id}")
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