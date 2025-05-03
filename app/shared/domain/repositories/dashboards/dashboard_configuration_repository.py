from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

# Assuming the entity model is correctly placed and importable
# TODO: Rename Entity import?
from app.shared.infrastructure.models.dashboards import DashboardConfigurationEntity

# TODO: Rename Interface
class DashboardConfigurationRepository(ABC):
    """Interface for accessing and managing dashboard configurations."""

    @abstractmethod
    async def get_by_id(self, config_id: int) -> Optional[DashboardConfigurationEntity]:
        """Retrieves a dashboard configuration by its unique ID."""
        pass

    @abstractmethod
    async def list_all(self) -> List[DashboardConfigurationEntity]:
        """Retrieves all dashboard configurations."""
        pass

    @abstractmethod
    async def create(self, 
                     name: str,
                     dashboard_type: str,
                     description: Optional[str] = None,
                     config: Optional[Dict[str, Any]] = None
                    ) -> DashboardConfigurationEntity:
        """Creates a new dashboard configuration."""
        pass

    @abstractmethod
    async def update(self, config_id: int, update_data: Dict[str, Any]) -> Optional[DashboardConfigurationEntity]:
        """Updates an existing dashboard configuration."""
        pass

    @abstractmethod
    async def delete(self, config_id: int) -> bool:
        """Deletes a dashboard configuration by ID. Returns True if successful."""
        pass 