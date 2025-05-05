from .system_monitoring_commands import setup
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

__all__ = ['setup']
