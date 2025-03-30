import logging
import os
from typing import Optional, Dict, Any, Type
from app.shared.infrastructure.logging.services.logging_service import LoggingService
from app.shared.infrastructure.logging.models import LogEntry
from app.shared.application.logging.log_config import get_config

class BaseLoggingService(LoggingService):
    """Base implementation of the logging service that uses Python's logging"""
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
        self._configure_logger()
    
    def _configure_logger(self) -> None:
        """Configure the logger with handlers based on current config"""
        # Set debug level based on environment
        is_development = os.getenv('ENVIRONMENT', '').lower() == 'development'
        default_level = logging.DEBUG if is_development else logging.INFO
        
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=default_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def log(self, message: str, level: str, **context) -> None:
        """Log a message with the specified level and context"""
        level_num = getattr(logging, level.upper())
        extra = context or {}
        self.logger.log(level_num, message, extra=extra)
    
    def info(self, message: str, **context) -> None:
        """Log an info message"""
        self.log(message, "INFO", **context)
    
    def error(self, message: str, exception: Optional[Exception] = None, **context) -> None:
        """Log an error message"""
        if exception:
            self.logger.exception(message, exc_info=exception)
        else:
            self.log(message, "ERROR", **context)
    
    def debug(self, message: str, **context) -> None:
        """Log a debug message"""
        # Only log debug messages in development environment
        if os.getenv('ENVIRONMENT', '').lower() == 'development':
            self.log(message, "DEBUG", **context)
    
    def warning(self, message: str, **context) -> None:
        """Log a warning message"""
        self.log(message, "WARNING", **context)
        
    def get_child(self, name: str) -> 'BaseLoggingService':
        """Get a child logger with the specified name"""
        logger_name = f"{self.logger.name}.{name}"
        return BaseLoggingService(logger_name)