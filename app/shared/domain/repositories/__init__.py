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
    DashboardRepository,
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
    'DashboardRepository',
    'GuildRepository',
    
    # Monitoring
    'MonitoringRepository',
    
    # Projects
    'ProjectRepository',
    'TaskRepository',
    
    # Utils
    'RateLimitRepository',
    
    # Audit
    'AuditLogRepository'
]