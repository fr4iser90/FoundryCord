# Export composite factories for top-level import
from .composite.bot_factory import BotComponentFactory
from .discord_ui.dashboard_factory import DashboardFactory

# Allow direct access to specific factories if needed
from .service.service_factory import ServiceFactory
from .service.task_factory import TaskFactory

# You may want to export the base factory as well
from .base.base_factory import BaseFactory

from .monitoring.collector_factory import CollectorFactory

__all__ = [
    'BotComponentFactory',
    'DashboardFactory',
    'ServiceFactory',
    'TaskFactory',
    'BaseFactory',
    'CollectorFactory'
]

