import logging
from logging.handlers import RotatingFileHandler
import os
import sys

# Create a function to set up the logger
def setup_logger():
    # Create logger
    logger = logging.getLogger('homelab_bot')
    logger.setLevel(logging.DEBUG)  # You can change this dynamically based on the environment

    # Define formatter for consistent log format
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler (for terminal output)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)  # Can be dynamically changed to INFO or ERROR
    ch.setFormatter(log_formatter)

    # File handler (for persistent logging)
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)  # Ensure the 'logs' directory exists
    fh = RotatingFileHandler(os.path.join(log_dir, 'homelab_bot.log'), maxBytes=10**6, backupCount=5)  # Rotate after 1MB
    fh.setLevel(logging.INFO)  # Info and above for file logs
    fh.setFormatter(log_formatter)

    # Optional: You can add more handlers here, such as a remote server handler

    # Add handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger

# Initialize the logger
logger = setup_logger()

# Usage: Anywhere in the codebase
# logger.debug('This is a debug message')
# logger.info('System is running smoothly')
# logger.warning('Disk space running low')
# logger.error('Error encountered while starting container')
# logger.critical('Critical failure in system')
