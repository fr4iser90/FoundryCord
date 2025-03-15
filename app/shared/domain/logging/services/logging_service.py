from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..entities.log_entry import LogEntry

class LoggingService(ABC):
    """Abstract base class for all logging services"""
    
    @abstractmethod
    def log(self, message: str, level: str, **context) -> None:
        """Log a message with the specified level and context"""
        pass
    
    @abstractmethod
    def info(self, message: str, **context) -> None:
        """Log an info message"""
        pass
    
    @abstractmethod
    def error(self, message: str, exception: Optional[Exception] = None, **context) -> None:
        """Log an error message"""
        pass
    
    @abstractmethod
    def debug(self, message: str, **context) -> None:
        """Log a debug message"""
        pass
    
    @abstractmethod
    def warning(self, message: str, **context) -> None:
        """Log a warning message"""
        pass