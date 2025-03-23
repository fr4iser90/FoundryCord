"""
Models for database storage.

Organized in domain-specific subpackages:
- core: Core system models (config, logging)
- auth: Authentication and user models
- discord: Discord-specific models
- dashboard: Dashboard UI models
- project: Project management models
- monitoring: System monitoring models
"""
from .base import Base

# Core models
from .core import Config, AuditLog, LogEntry

# Auth models
from .auth import User, Session, RateLimit, Role

# Discord models
from .discord import ChannelMapping, CategoryMapping, AutoThreadChannelEntity, GuildConfigEntity, GuildEntity, MessageEntity, GuildUserEntity, ChannelEntity, ChannelPermissionEntity, CategoryEntity, CategoryPermissionEntity

# Dashboard models
from .dashboards import Dashboard, DashboardComponent, ComponentLayout, ContentTemplate, DashboardMessage

# Project models 
from .project import Project, Task, ProjectMember

# Monitoring models
from .monitoring import MetricModel, AlertModel

# Export all models for convenient imports elsewhere
__all__ = [
    # Base class
    'Base',
    # Core models
    'Config', 'AuditLog', 'LogEntry',
    # Auth models
    'User', 'Session', 'RateLimit', 'Role',
    # Discord models
    'ChannelMapping', 'CategoryMapping', 'AutoThreadChannelEntity', 'GuildConfigEntity', 'GuildEntity', 'MessageEntity', 'GuildUserEntity', 'ChannelEntity', 'ChannelPermissionEntity', 'CategoryEntity', 'CategoryPermissionEntity',
    # Dashboard models
    'Dashboard', 'DashboardComponent', 'ComponentLayout', 'ContentTemplate', 'DashboardMessage',
    # Project models
    'Project', 'Task', 'ProjectMember',
    # Monitoring models
    'MetricModel', 'AlertModel'
]
