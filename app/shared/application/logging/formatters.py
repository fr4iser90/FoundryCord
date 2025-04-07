import logging
import json
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """
    Format logs as JSON strings for structured logging
    """
    def __init__(self, fields: Dict[str, Any] = None):
        super().__init__()
        self.fields = fields or {}
        
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        # Add custom fields
        for key, value in self.fields.items():
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
                
        # Add any extra attributes from the LogRecord
        for key, value in record.__dict__.items():
            if key not in log_data and not key.startswith('_'):
                log_data[key] = value
                
        return json.dumps(log_data)

class DetailedFormatter(logging.Formatter):
    """
    Format logs with detailed information about code location
    """
    def __init__(self, fmt=None, datefmt=None):
        if fmt is None:
            fmt = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d - %(funcName)s) - %(message)s"
        super().__init__(fmt=fmt, datefmt=datefmt)

class CompactFormatter(logging.Formatter):
    """
    Format logs with minimal information for cleaner output
    """
    def __init__(self, datefmt=None):
        fmt = "%(asctime)s [%(levelname).1s] %(message)s"  # Kürzeres Format mit nur einem Buchstaben für Level
        super().__init__(fmt=fmt, datefmt=datefmt)
        
    def formatTime(self, record, datefmt=None):
        """Override to use shorter time format"""
        if datefmt is None:
            datefmt = "%H:%M:%S"  # Nur Zeit, kein Datum
        return super().formatTime(record, datefmt)
