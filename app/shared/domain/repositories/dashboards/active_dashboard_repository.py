"""Domain Interface for accessing Active Dashboard Instances."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

# Import the corresponding Entity - use forward reference if needed to avoid circular imports
# from app.shared.infrastructure.models.dashboards import ActiveDashboardEntity

class ActiveDashboardRepository(ABC):
    """Interface for repository handling active dashboard instances."""

    @abstractmethod
    async def get_by_id(self, instance_id: int) -> Optional['ActiveDashboardEntity']: # Use forward reference
        """Retrieves an active dashboard instance by its unique ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_channel_id(self, channel_id: str) -> Optional['ActiveDashboardEntity']:
        """Retrieves an active dashboard instance by its channel ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_active_by_guild(self, guild_id: str) -> List['ActiveDashboardEntity']:
        """Retrieves all active dashboard instances for a specific guild."""
        raise NotImplementedError

    @abstractmethod
    async def list_all_active(self) -> List['ActiveDashboardEntity']:
        """Retrieves all active dashboard instances across all guilds."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, config_id: int, guild_id: str, channel_id: str, message_id: Optional[str] = None, is_active: bool = True, config_override: Optional[Dict[str, Any]] = None) -> 'ActiveDashboardEntity':
        """Creates a new active dashboard instance."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, instance_id: int, update_data: Dict[str, Any]) -> Optional['ActiveDashboardEntity']:
        """Updates an existing active dashboard instance."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, instance_id: int) -> bool:
        """Deletes an active dashboard instance by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def set_message_id(self, instance_id: int, message_id: Optional[str]) -> bool:
        """Sets or updates the message_id for an active dashboard instance."""
        raise NotImplementedError

    @abstractmethod
    async def set_active_status(self, instance_id: int, is_active: bool) -> bool:
        """Sets the active status for a dashboard instance."""
        raise NotImplementedError 