"""
Models for database storage.

Organized in domain-specific subpackages:
- core: Core system models (config, logging)
- auth: Authentication and user models
- discord: Discord-specific models
- dashboard: Dashboard UI models
- project: Project management models
- monitoring: System monitoring models
- ui: General UI related models (like layouts)
"""
from .base import Base

# Core models
from .core import ConfigEntity, AuditLogEntity, LogEntryEntity

# Auth models
from .auth import AppUserEntity, SessionEntity, RateLimitEntity, AppRoleEntity

# Discord models
from .discord import ChannelMapping, CategoryMapping, AutoThreadChannelEntity, GuildConfigEntity, GuildEntity, MessageEntity, DiscordGuildUserEntity, ChannelEntity, ChannelPermissionEntity, CategoryEntity, CategoryPermissionEntity

# Dashboard models
from .dashboards import DashboardEntity, DashboardComponentEntity, ComponentLayoutEntity, ContentTemplateEntity, DashboardMessageEntity

# Project models 
from .project import Project, Task, ProjectMember

# Monitoring models
from .monitoring import MetricModel, AlertModel

# UI Models
from .ui import UILayoutEntity, SharedUILayoutTemplateEntity

# Export all models for convenient imports elsewhere
__all__ = [
    # Base class
    'Base',
    # Core models
    'ConfigEntity', 'AuditLogEntity', 'LogEntryEntity',
    # Auth models
    'AppUserEntity', 'SessionEntity', 'RateLimitEntity', 'AppRoleEntity',
    # Discord models
    'ChannelMapping', 'CategoryMapping', 'AutoThreadChannelEntity', 'GuildConfigEntity', 'GuildEntity', 'MessageEntity', 'DiscordGuildUserEntity', 'ChannelEntity', 'ChannelPermissionEntity', 'CategoryEntity', 'CategoryPermissionEntity',
    # Dashboard models
    'DashboardEntity', 'DashboardComponentEntity', 'ComponentLayoutEntity', 'ContentTemplateEntity', 'DashboardMessageEntity',
    # Project models
    'Project', 'Task', 'ProjectMember',
    # Monitoring models
    'MetricModel', 'AlertModel',
    # UI Models
    'UILayoutEntity', 'SharedUILayoutTemplateEntity'
]
