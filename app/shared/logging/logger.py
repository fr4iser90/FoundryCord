import logging
from logging.handlers import RotatingFileHandler
import os
import sys

# Track which loggers have been configured
_configured_loggers = set()

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
    
    # Disable propagation to parent loggers to prevent duplicate logs
    logger.propagate = False
    
    # Set base level to DEBUG to catch all messages
    logger.setLevel(logging.DEBUG)

    # Get environment from env variable, default to 'production'
    environment = os.getenv('ENVIRONMENT', 'production').lower()
    
    # Define formatter
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler (for Terminal output)
    ch = logging.StreamHandler(sys.stdout)
    # Set console level based on environment
    if environment == 'development':
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)  # In production, only show INFO and above
    ch.setFormatter(log_formatter)
    logger.addHandler(ch)

    try:
        # File handler (for persistent logs)
        log_dir = './logs'
        os.makedirs(log_dir, exist_ok=True)  # Create logs directory if it doesn't exist
        
        # Debug log file (only in development)
        if environment == 'development':
            debug_fh = RotatingFileHandler(
                os.path.join(log_dir, f'debug_{component if component else "main"}.log'),
                maxBytes=10**6,
                backupCount=3
            )
            debug_fh.setLevel(logging.DEBUG)
            debug_fh.setFormatter(log_formatter)
            logger.addHandler(debug_fh)

        # Main log file (for INFO and above)
        fh = RotatingFileHandler(
            os.path.join(log_dir, log_filename),
            maxBytes=10**6,
            backupCount=5
        )
        fh.setLevel(logging.INFO)
        fh.setFormatter(log_formatter)
        logger.addHandler(fh)
    except Exception as e:
        print(f"Could not create file handler: {e}")
        # We don't log this error to avoid circular dependencies
    
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