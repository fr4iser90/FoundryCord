"""
Dashboard related Application Services.
"""

from .dashboard_component_service import DashboardComponentService
from .dashboard_configuration_service import DashboardConfigurationService
# Add other dashboard services here if created later

__all__ = [
    'DashboardComponentService',
    'DashboardConfigurationService',
] 