"""
Abstract Repository Interface for Dashboard Component Definitions.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

# Import the entity type it operates on
from app.shared.infrastructure.models.dashboards import DashboardComponentDefinitionEntity

class DashboardComponentDefinitionRepository(ABC):
    """Interface for accessing dashboard component definitions data."""

    @abstractmethod
    async def list_definitions(
        self,
        dashboard_type: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> List[DashboardComponentDefinitionEntity]:
        """Retrieves a list of component definitions, optionally filtered.

        Args:
            dashboard_type: Filter by dashboard type (e.g., 'common', 'welcome').
            component_type: Filter by component type (e.g., 'button', 'embed').

        Returns:
            A list of matching DashboardComponentDefinitionEntity objects.
        """
        pass 