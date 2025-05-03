"""
Central Repository Interface Module
All repository interfaces are exported from here to provide a single import point
"""

from .base_repository import BaseRepository

# Auth repositories
from .auth import (
    UserRepository,
    SessionRepository,
    KeyRepository
)

# Discord repositories
from .discord import (
    ChannelRepository,
    CategoryRepository,
    GuildConfigRepository,
    GuildRepository
)

# Monitoring repositories
from .monitoring import MonitoringRepository

# Project repositories
from .projects import (
    ProjectRepository,
    TaskRepository
)

# Utility repositories
from .utils import RateLimitRepository

# Audit repositories
from .audit import AuditLogRepository

# Import the new dashboard repository interfaces
from .dashboards import (
    ActiveDashboardRepository,
    DashboardConfigurationRepository,
    DashboardComponentDefinitionRepository,
)

__all__ = [
    # Base
    'BaseRepository',
    
    # Auth
    'UserRepository',
    'SessionRepository',
    'KeyRepository',
    
    # Discord
    'ChannelRepository',
    'CategoryRepository',
    'GuildConfigRepository',
    'GuildRepository',
    
    # Monitoring
    'MonitoringRepository',
    
    # Projects
    'ProjectRepository',
    'TaskRepository',
    
    # Utils
    'RateLimitRepository',
    
    # Audit
    'AuditLogRepository',

    # Dashboards (New)
    'ActiveDashboardRepository',
    'DashboardConfigurationRepository',
    'DashboardComponentDefinitionRepository',
]