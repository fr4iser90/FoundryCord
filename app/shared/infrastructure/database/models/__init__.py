# Import the Base class
from .base import Base

# Import all models to expose them
from .auth_models import User, Session, RateLimit
from .audit_models import AuditLog
from .discord_models import ChannelMapping, CategoryMapping
from .dashboard_models import DashboardMessage  # Legacy model
from .dashboards import Dashboard, DashboardComponent, ComponentLayout, ContentTemplate  # New models
from .project_models import Project, Task
from .monitoring_models import MetricModel, AlertModel

# Export all models for convenient imports elsewhere
__all__ = [
    'Base',
    'User', 
    'Session', 
    'RateLimit', 
    'AuditLog',
    'ChannelMapping',
    'CategoryMapping',
    'DashboardMessage',  # Legacy
    'Dashboard',
    'DashboardComponent',
    'ComponentLayout',
    'ContentTemplate',
    'Project',
    'Task',
    'MetricModel',
    'AlertModel'
]
