from typing import Optional, Dict, Any
from app.shared.domain.audit.services.logging_service import LoggingService
from app.shared.application.logging.log_config import update_config
import inspect
# Don't import factories directly
# from app.shared.interface.logging.factories import create_bot_logging_service, create_web_logging_service

# Default service instances
_bot_service: Optional[LoggingService] = None
_web_service: Optional[LoggingService] = None
_db_service: Optional[LoggingService] = None

def get_module_logger(module_name: Optional[str] = None) -> LoggingService:
    """
    Get a logger based on module name, auto-detecting if not provided.
    
    Args:
        module_name: Optional module name. If None, automatically detects caller module.
        
    Returns:
        Configured LoggingService instance
    """
    if not module_name:
        # Auto-detect the calling module's name
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        if mod:
            module_name = mod.__name__
            # Strip app prefix for cleaner names
            if module_name.startswith('app.'):
                module_name = module_name[4:]
        else:
            module_name = "unknown"
    
    # Use the bot service as the base
    logger = get_bot_logger()
    # Return a child logger with the module name
    return logger.get_child(module_name)

def get_bot_logger(name: str = "homelab.bot") -> LoggingService:
    """Get the bot logging service"""
    global _bot_service
    if _bot_service is None:
        from app.shared.infrastructure.logging.services.base_logging_service import BaseLoggingService
        _bot_service = BaseLoggingService(name)
    return _bot_service

def get_web_logger(name: str = "homelab.web") -> LoggingService:
    """Get the web logging service"""
    global _web_service
    if _web_service is None:
        from app.shared.infrastructure.logging.services.base_logging_service import BaseLoggingService
        _web_service = BaseLoggingService(name)
    return _web_service

def get_db_logger(name: str = "homelab.db") -> LoggingService:
    """Get the database logging service"""
    global _db_service
    if _db_service is None:
        from app.shared.infrastructure.logging.services.base_logging_service import BaseLoggingService
        _db_service = BaseLoggingService(name)
    return _db_service

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
    # Import the factory function only when needed
    from app.shared.interface.logging.factories import create_bot_logging_service
    service = create_bot_logging_service(bot)
    bot.add_cog(service)
    global _bot_service
    _bot_service = service
    return service

def setup_web_logging(app) -> LoggingService:
    """Set up web logging"""
    # Import the factory function only when needed
    from app.shared.interface.logging.factories import create_web_logging_service
    service = create_web_logging_service(app)
    service.setup_request_logging()
    global _web_service
    _web_service = service
    return service