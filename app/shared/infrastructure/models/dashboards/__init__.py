"""
Dashboard models for the database.
"""
# Keep only the models relevant to the new structure
from .active_dashboard_entity import ActiveDashboardEntity
from .dashboard_component_definition_entity import DashboardComponentDefinitionEntity
from .dashboard_configuration_entity import DashboardConfigurationEntity

__all__ = [
    'ActiveDashboardEntity',
    'DashboardComponentDefinitionEntity',
    'DashboardConfigurationEntity'
]