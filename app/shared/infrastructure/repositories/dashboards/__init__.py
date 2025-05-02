"""
Dashboard related Infrastructure Repositories Implementations.
"""

from .dashboard_component_definition_repository_impl import DashboardComponentDefinitionRepositoryImpl
from .dashboard_configuration_repository_impl import DashboardConfigurationRepositoryImpl

# Add other dashboard repository implementations here if created later

__all__ = [
    'DashboardComponentDefinitionRepositoryImpl',
    'DashboardConfigurationRepositoryImpl',
] 