# Export services for top-level package imports

# Category setup
from .category_setup.category_setup_service import CategorySetupService
from .channel.game_server_channel_service import GameServerChannelService
from .channel_setup.channel_setup_service import ChannelSetupService
from .config.config_service import ConfigService

# Dashboard services
from .dashboard.dashboard_builder import DashboardBuilder
from .dashboard.dashboard_builder_service import DashboardBuilderService
from .dashboard.dashboard_lifecycle_service import DashboardLifecycleService
from .dashboard.dashboard_repository import DashboardRepository
from .dashboard.dashboard_service import DashboardService

# Monitoring services
from .monitoring.system_monitoring import SystemMonitoringService
from .system_metrics.system_metrics_service import SystemMetricsService

# VPN services
from .wireguard.wireguard_service import WireguardService

# Make all services available at the module level
__all__ = [
    'CategorySetupService',
    'GameServerChannelService',
    'ChannelSetupService',
    'ConfigService',
    
    # Dashboard infrastructure
    'DashboardBuilder',
    'DashboardBuilderService',
    'DashboardLifecycleService', 
    'DashboardRepository',
    'DashboardService',
    
    # System services
    'SystemMonitoringService',
    'SystemMetricsService',
    'WireguardService',
]
