import logging
from logging.handlers import RotatingFileHandler
import os
import sys

def setup_logger():
    # Create logger
    logger = logging.getLogger('homelab_bot')
    
    # Get environment from env variable, default to 'production'
    environment = os.getenv('ENVIRONMENT', 'production').lower()
    
    # Set base level to DEBUG to catch all messages
    logger.setLevel(logging.DEBUG)

    # Define formatter
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler (für Terminal output)
    ch = logging.StreamHandler(sys.stdout)
    # Set console level based on environment
    if environment == 'development':
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)  # In production, only show INFO and above
    ch.setFormatter(log_formatter)
    logger.addHandler(ch)

    try:
        # File handler (für persistente Logs)
        log_dir = './logs'
        os.makedirs(log_dir, exist_ok=True)  # Create logs directory if it doesn't exist
        
        # Debug log file (only in development)
        if environment == 'development':
            debug_fh = RotatingFileHandler(
                os.path.join(log_dir, 'debug.log'),
                maxBytes=10**6,
                backupCount=3
            )
            debug_fh.setLevel(logging.DEBUG)
            debug_fh.setFormatter(log_formatter)
            logger.addHandler(debug_fh)

        # Main log file (for INFO and above)
        fh = RotatingFileHandler(
            os.path.join(log_dir, 'homelab_bot.log'),
            maxBytes=10**6,
            backupCount=5
        )
        fh.setLevel(logging.INFO)
        fh.setFormatter(log_formatter)
        logger.addHandler(fh)
    except Exception as e:
        logger.error(f"Konnte File Handler nicht erstellen: {e}")
        # Wir loggen den Fehler, aber der Logger funktioniert weiter mit Console Output

    return logger

# Initialize the logger
logger = setup_logger()