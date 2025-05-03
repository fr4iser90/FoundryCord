"""
Dashboard related Domain Repositories Interfaces.
"""

from .active_dashboard_repository import ActiveDashboardRepository
from .dashboard_configuration_repository import DashboardConfigurationRepository
from .dashboard_component_definition_repository import DashboardComponentDefinitionRepository

__all__ = [
    'ActiveDashboardRepository',
    'DashboardConfigurationRepository',
    'DashboardComponentDefinitionRepository',
] 