# app/shared/infrastructure/repositories/__init__.py
"""
Central Repository Implementation Module
All repository implementations are exported from here to provide a single import point
"""

# Auth implementations
from .auth import (
    UserRepositoryImpl,
    SessionRepositoryImpl,
    KeyRepositoryImpl
)

# Discord implementations
from .discord import (
    ChannelRepositoryImpl,
    CategoryRepositoryImpl,
    GuildConfigRepositoryImpl,
    DashboardRepositoryImpl,
    GuildRepositoryImpl
)

# Monitoring implementations
from .monitoring import MonitoringRepositoryImpl

# Project implementations
from .projects import (
    ProjectRepositoryImpl,
    TaskRepositoryImpl
)

# UI implementations
from .ui import UILayoutRepositoryImpl

# Utility implementations
from .utils import RateLimitRepositoryImpl

# Audit implementations
from .audit import AuditLogRepositoryImpl

# Guild Template implementations
from .guild_templates import (
    GuildTemplateRepositoryImpl,
    GuildTemplateCategoryRepositoryImpl,
    GuildTemplateChannelRepositoryImpl,
    GuildTemplateCategoryPermissionRepositoryImpl,
    GuildTemplateChannelPermissionRepositoryImpl,
    DashboardConfigurationRepositoryImpl
)

# NEW: Dashboard Component Definition implementation
from .dashboards import DashboardComponentDefinitionRepositoryImpl

# Base implementation
from .base_repository_impl import BaseRepositoryImpl

__all__ = [
    # Base
    'BaseRepositoryImpl',
    
    # Auth
    'UserRepositoryImpl',
    'SessionRepositoryImpl',
    'KeyRepositoryImpl',
    
    # Discord
    'ChannelRepositoryImpl',
    'CategoryRepositoryImpl',
    'GuildConfigRepositoryImpl',
    'DashboardRepositoryImpl',
    'GuildRepositoryImpl',

    # Guild Templates
    'GuildTemplateRepositoryImpl',
    'GuildTemplateCategoryRepositoryImpl',
    'GuildTemplateChannelRepositoryImpl',
    'GuildTemplateCategoryPermissionRepositoryImpl',
    'GuildTemplateChannelPermissionRepositoryImpl',
    'DashboardConfigurationRepositoryImpl',
    
    # Monitoring
    'MonitoringRepositoryImpl',
    
    # Projects
    'ProjectRepositoryImpl',
    'TaskRepositoryImpl',

    # UI
    'UILayoutRepositoryImpl',
    
    # Utils
    'RateLimitRepositoryImpl',
    
    # Audit
    'AuditLogRepositoryImpl',

    # NEW: Dashboard Component Definitions
    'DashboardComponentDefinitionRepositoryImpl',
]