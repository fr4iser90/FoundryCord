# Export services for top-level package imports

# Category services
from .category.category_builder import CategoryBuilder
from .category.category_setup_service import CategorySetupService

# Channel services
from .channel.channel_builder import ChannelBuilder
from .channel.channel_factory import ChannelFactory
from .channel.channel_setup_service import ChannelSetupService
from .channel.game_server_channel_service import GameServerChannelService

# Configuration services
from .config.config_service import ConfigService

# Dashboard services
from .dashboard.dashboard_builder import DashboardBuilder
from .dashboard.dashboard_builder_service import DashboardBuilderService
from .dashboard.dashboard_lifecycle_service import DashboardLifecycleService
from .dashboard.dashboard_repository import DashboardRepository
from .dashboard.dashboard_service import DashboardService
from .dashboard.component_loader_service import ComponentLoaderService

# --- Add Discord Services --- 
from .discord.discord_query_service import DiscordQueryService
# --------------------------

# Monitoring services
from .monitoring.system_monitoring import SystemMonitoringService
from .system_metrics.system_metrics_service import SystemMetricsService

# Project management services
from .project_management.project_service import ProjectService
from .project_management.task_service import TaskService

# VPN services
from .wireguard.wireguard_service import WireguardService

# Make all services available at the module level
__all__ = [
    # Category services
    'CategoryBuilder',
    'CategorySetupService',
    
    # Channel services
    'ChannelBuilder',
    'ChannelFactory',
    'ChannelSetupService',
    'GameServerChannelService',
    
    # Configuration services
    'ConfigService',
    
    # Dashboard services
    'DashboardBuilder',
    'DashboardBuilderService',
    'DashboardLifecycleService', 
    'DashboardRepository',
    'DashboardService',
    'ComponentLoaderService',

    # --- Add Discord Services to __all__ --- 
    'DiscordQueryService',
    # --------------------------------------
    
    # Project management services
    'ProjectService',
    'TaskService',
    
    # System services
    'SystemMonitoringService',
    'SystemMetricsService',
    'WireguardService',
]
