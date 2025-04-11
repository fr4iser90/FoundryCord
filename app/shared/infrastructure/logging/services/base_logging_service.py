import logging
import os
from typing import Optional, Dict, Any
from app.shared.infrastructure.logging.services.logging_service import LoggingService
from app.shared.infrastructure.logging.models import LogEntry
from app.shared.application.logging.log_config import get_config

class BaseLoggingService(LoggingService):
    """Base implementation of the logging service that uses Python's logging"""
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
        # Configure logging if not already done
        if not logging.getLogger().handlers:
            get_config().configure_logging()
    
    def log(self, message: str, level: str, **context) -> None:
        """Log a message with the specified level and context"""
        level_num = getattr(logging, level.upper())
        extra = context or {}
        # Prevent potential exc_info conflict even in basic log calls if context might contain it
        if 'exc_info' in extra:
             self.logger.warning("Removed conflicting 'exc_info' from context in basic log call.", extra={'original_context': extra.copy()})
             extra.pop('exc_info')
        self.logger.log(level_num, message, extra=extra)
    
    def debug(self, message: str, **context) -> None:
        """Log a debug message"""
        # Only log debug messages in development environment
        if os.getenv('ENVIRONMENT', '').lower() == 'development':
            self.log(message, "DEBUG", **context)
    
    def info(self, message: str, **context) -> None:
        """Log an info message"""
        self.log(message, "INFO", **context)
    
    def error(self, message: str, exception: Optional[Exception] = None, **context) -> None:
        """Log an error message, handling potential exc_info conflict."""
        extra = context or {}
        # Explicitly remove exc_info from context before passing to logger.error/exception
        if 'exc_info' in extra:
            self.logger.warning("Removed conflicting 'exc_info' from context before logging error.", extra={'original_context': extra.copy()})
            popped_exc_info = extra.pop('exc_info')
            # Decide which exc_info to use: the one passed explicitly or the one from context?
            # Typically, the explicit one (or True/exception object) takes precedence.
            final_exc_info = exception or popped_exc_info or True 
        else:
            final_exc_info = exception or True # Default for error logging

        if exception: # Prefer logger.exception if an exception object is available
            self.logger.exception(message, exc_info=final_exc_info, extra=extra)
        else:
             # Log as error, potentially with traceback if final_exc_info is True/Exception
             self.logger.error(message, exc_info=final_exc_info, extra=extra)
    
    def exception(self, message: str, exception: Optional[Exception] = None, **context) -> None:
        """Log an exception message, ensuring no exc_info conflict."""
        extra = context or {}
        final_exc_info = exception or True # exception() always implies traceback

        # --- FIX: Explicitly remove exc_info from context --- 
        if 'exc_info' in extra:
            self.logger.warning("Removed conflicting 'exc_info' from context before logger.exception call.", extra={'original_context': extra.copy()})
            extra.pop('exc_info')
        # --- END FIX ---
            
        # Call logger.exception with guaranteed clean context and correct exc_info value
        self.logger.exception(message, exc_info=final_exc_info, extra=extra)
    
    def warning(self, message: str, **context) -> None:
        """Log a warning message"""
        self.log(message, "WARNING", **context)
    
    def get_child(self, name: str) -> 'BaseLoggingService':
        """Get a child logger with the specified name"""
        logger_name = f"{self.logger.name}.{name}"
        return BaseLoggingService(logger_name)