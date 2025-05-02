from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

# Assuming the new entity model is correctly placed and importable
from app.shared.infrastructure.models.guild_templates import TemplateDashboardInstanceEntity

class TemplateDashboardInstanceRepository(ABC):
    """Interface for accessing and managing template dashboard instances in the database."""

    @abstractmethod
    async def get_by_id(self, instance_id: int) -> Optional[TemplateDashboardInstanceEntity]:
        """Retrieves a dashboard instance by its unique ID."""
        pass

    @abstractmethod
    async def get_by_template_channel_id(self, channel_template_id: int) -> List[TemplateDashboardInstanceEntity]:
        """Retrieves all dashboard instances linked to a specific guild template channel ID."""
        pass

    @abstractmethod
    async def create_for_template(self, 
                                  guild_template_channel_id: int,
                                  name: str,
                                  dashboard_type: str,
                                  config: Optional[Dict[str, Any]] = None
                                 ) -> TemplateDashboardInstanceEntity:
        """Creates a new dashboard instance linked to a template channel."""
        pass

    @abstractmethod
    async def update(self, instance_id: int, update_data: Dict[str, Any]) -> Optional[TemplateDashboardInstanceEntity]:
        """Updates an existing dashboard instance with the provided data."""
        pass

    @abstractmethod
    async def delete(self, instance_id: int) -> bool:
        """Deletes a dashboard instance by its ID. Returns True if deletion was successful, False otherwise."""
        pass 