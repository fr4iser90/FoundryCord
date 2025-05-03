"""Domain Interface for accessing Dashboard Configurations."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

# Use forward reference for the entity type
# from app.shared.infrastructure.models.dashboards import DashboardConfigurationEntity

class DashboardConfigurationRepository(ABC):
    """Interface for repository handling dashboard configurations/templates."""

    @abstractmethod
    async def get_by_id(self, config_id: int) -> Optional['DashboardConfigurationEntity']:
        """Retrieves a dashboard configuration by its unique ID."""
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> List['DashboardConfigurationEntity']:
        """Retrieves all dashboard configurations."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_name(self, name: str) -> Optional['DashboardConfigurationEntity']:
        """Retrieves a dashboard configuration by its unique name."""
        raise NotImplementedError

    @abstractmethod
    async def create(
        self,
        name: str,
        dashboard_type: str,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> 'DashboardConfigurationEntity':
        """Creates a new dashboard configuration."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, config_id: int, update_data: Dict[str, Any]) -> Optional['DashboardConfigurationEntity']:
        """Updates an existing dashboard configuration."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, config_id: int) -> bool:
        """Deletes a dashboard configuration by its ID."""
        raise NotImplementedError 