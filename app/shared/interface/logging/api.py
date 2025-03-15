from typing import Optional, Dict, Any
from ..domain.services.logging_service import LoggingService
from ..application.log_config import update_config
from .factories import create_bot_logging_service, create_web_logging_service

# Default service instances
_bot_service: Optional[LoggingService] = None
_web_service: Optional[LoggingService] = None
_db_service: Optional[LoggingService] = None

def get_bot_logger() -> LoggingService:
    """Get the bot logging service"""
    global _bot_service
    if _bot_service is None:
        from ..infrastructure.services.base_logging_service import BaseLoggingService
        _bot_service = BaseLoggingService("homelab.bot")
    return _bot_service

def get_web_logger() -> LoggingService:
    """Get the web logging service"""
    global _web_service
    if _web_service is None:
        from ..infrastructure.services.base_logging_service import BaseLoggingService
        _web_service = BaseLoggingService("homelab.web")
    return _web_service

def configure_logging(config: Dict[str, Any]) -> None:
    """Update the logging configuration"""
    update_config(config)

def enable_db_logging(level: str = "WARNING") -> None:
    """Enable database logging"""
    configure_logging({
        "log_to_db": True,
        "db_level": level,
        "handlers": ["console", "file", "db"]
    })

async def setup_bot_logging(bot) -> LoggingService:
    """Set up bot logging"""
    service = create_bot_logging_service(bot)
    bot.add_cog(service)
    global _bot_service
    _bot_service = service
    return service

def setup_web_logging(app) -> LoggingService:
    """Set up web logging"""
    service = create_web_logging_service(app)
    service.setup_request_logging()
    global _web_service
    _web_service = service
    return service