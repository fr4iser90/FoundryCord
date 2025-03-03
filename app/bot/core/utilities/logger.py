import logging
from logging.handlers import RotatingFileHandler
import os
import sys

def setup_logger():
    # Create logger
    logger = logging.getLogger('homelab_bot')
    logger.setLevel(logging.DEBUG)

    # Define formatter
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler (für Terminal output)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(log_formatter)
    logger.addHandler(ch)

    try:
        # File handler (für persistente Logs)
        log_dir = '/app/bot/logs'  # Absoluter Pfad statt relativer Pfad
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