import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from typing import Dict, Any, Optional, List

# Track which loggers have been configured
_configured_loggers = set()

# Default configuration
DEFAULT_LOG_CONFIG = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s", # TAG-MONAT STUNDE:MINUTE:SEKUNDE
    #"date_format": "%Y-%m-%d %H:%M:%S", # YYYY-MM-DD HH:MM:SS
    "date_format": "%d-%m %H:%M:%S", # DD-MM HH:MM:SS
    "console_level": "INFO",
    "file_level": "INFO",
    "debug_level": "DEBUG",
    "max_bytes": 1_000_000,  # 1MB
    "backup_count": 5,
    "log_to_db": False,
    "db_level": "WARNING",
    "handlers": ["console", "file"]  # Available: console, file, db
}

# Global configuration that can be updated at runtime
log_config = DEFAULT_LOG_CONFIG.copy()

def set_log_config(config: Dict[str, Any]) -> None:
    """
    Update the global logging configuration
    
    Args:
        config: Dictionary with configuration values to update
    """
    global log_config
    log_config.update(config)
    
    # Clear configured loggers to force reconfiguration with new settings
    _configured_loggers.clear()

def get_formatter(custom_format: Optional[str] = None, 
                 date_format: Optional[str] = None) -> logging.Formatter:
    """Get a formatter with the specified or default format"""
    log_format = custom_format or log_config["format"]
    date_fmt = date_format or log_config["date_format"]
    return logging.Formatter(log_format, datefmt=date_fmt)

def setup_logger(component=None):
    """
    Setup a logger with component-specific configuration
    
    Args:
        component (str, optional): Component name ('bot', 'web', 'db'). Defaults to None.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger with component name if provided
    if component:
        logger_name = f'homelab.{component}'
        log_filename = f'homelab_{component}.log'
    else:
        logger_name = 'homelab'
        log_filename = 'homelab.log'
        
    logger = logging.getLogger(logger_name)
    
    # Check our custom tracking set to prevent duplicate configuration
    if logger_name in _configured_loggers:
        return logger
    
    # Remove any existing handlers (in case of reconfiguration)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    
    # Disable propagation to parent loggers to prevent duplicate logs
    logger.propagate = False
    
    # Set base level to DEBUG to catch all messages
    logger.setLevel(logging.DEBUG)

    # Get environment from env variable, default to 'production'
    environment = os.getenv('ENVIRONMENT', 'production').lower()
    
    # Define formatter
    log_formatter = get_formatter()

    # Set up requested handlers
    if "console" in log_config["handlers"]:
        # Console handler (for Terminal output)
        ch = logging.StreamHandler(sys.stdout)
        # Set console level based on environment and config
        if environment == 'development':
            ch.setLevel(getattr(logging, log_config["debug_level"]))
        else:
            ch.setLevel(getattr(logging, log_config["console_level"]))
        ch.setFormatter(log_formatter)
        logger.addHandler(ch)

    if "file" in log_config["handlers"]:
        try:
            # File handler (for persistent logs)
            log_dir = './logs'
            os.makedirs(log_dir, exist_ok=True)  # Create logs directory if it doesn't exist
            
            # Debug log file (only in development)
            if environment == 'development':
                debug_fh = RotatingFileHandler(
                    os.path.join(log_dir, f'debug_{component if component else "main"}.log'),
                    maxBytes=log_config["max_bytes"],
                    backupCount=log_config["backup_count"]
                )
                debug_fh.setLevel(getattr(logging, log_config["debug_level"]))
                debug_fh.setFormatter(log_formatter)
                logger.addHandler(debug_fh)

            # Main log file (for INFO and above)
            fh = RotatingFileHandler(
                os.path.join(log_dir, log_filename),
                maxBytes=log_config["max_bytes"],
                backupCount=log_config["backup_count"]
            )
            fh.setLevel(getattr(logging, log_config["file_level"]))
            fh.setFormatter(log_formatter)
            logger.addHandler(fh)
        except Exception as e:
            print(f"Could not create file handler: {e}")
            # We don't log this error to avoid circular dependencies
    
    # DB handler is added only if explicitly configured
    if "db" in log_config["handlers"] and log_config["log_to_db"]:
        try:
            from .handlers.db_handler import DatabaseHandler
            db_handler = DatabaseHandler()
            db_handler.setLevel(getattr(logging, log_config["db_level"]))
            db_handler.setFormatter(log_formatter)
            logger.addHandler(db_handler)
        except ImportError:
            print("Database handler module not available")
        except Exception as e:
            print(f"Could not create database handler: {e}")
    
    # Mark this logger as configured
    _configured_loggers.add(logger_name)
    
    return logger

# Initialize the loggers only once
root_logger = setup_logger()
bot_logger = setup_logger('bot')
web_logger = setup_logger('web')
db_logger = setup_logger('db')

# For backward compatibility
logger = bot_logger