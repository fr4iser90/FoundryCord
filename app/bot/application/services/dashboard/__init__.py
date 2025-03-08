from .welcome_dashboard_service import WelcomeDashboardService, setup as welcome_setup
from .monitoring_dashboard_service import MonitoringDashboardService, setup as monitoring_setup
from .project_dashboard_service import ProjectDashboardService, setup as project_setup
from .general_dashboard_service import GeneralDashboardService, setup as general_setup

__all__ = [
    'WelcomeDashboardService',
    'MonitoringDashboardService',
    'ProjectDashboardService',
    'GeneralDashboardService',
    'welcome_setup',
    'monitoring_setup',
    'project_setup',
    'general_setup'
]
