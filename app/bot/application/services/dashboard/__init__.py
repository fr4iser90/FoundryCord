from .welcome_dashboard_service import WelcomeDashboardService, setup as welcome_setup
from .monitoring_dashboard_service import MonitoringDashboardService, setup as monitoring_setup
from .project_dashboard_service import ProjectDashboardService, setup as project_setup
from .gameservers_dashboard_service import GameServerDashboardService, setup as gameservers_setup
from .dynamic_minecraft_dashboard_service import DynamicMinecraftDashboardService, setup as dynamic_minecraft_setup

__all__ = [
    'WelcomeDashboardService',
    'MonitoringDashboardService',
    'ProjectDashboardService',
    'GameServerDashboardService',
    'DynamicMinecraftDashboardService',
    'welcome_setup',
    'monitoring_setup',
    'project_setup',
    'gameservers_setup',
    'dynamic_minecraft_setup'
]
