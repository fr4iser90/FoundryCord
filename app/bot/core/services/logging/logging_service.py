import logging
from logging.handlers import RotatingFileHandler
import os
import sys

class LoggingService:
    def __init__(self, bot):
        self.bot = bot
        self.logger = self._setup_logger()

    def _setup_logger(self):
        # Create logger
        logger = logging.getLogger('homelab_bot')
        logger.setLevel(logging.DEBUG)

        # Define formatter
        log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(log_formatter)
        logger.addHandler(ch)

        try:
            # File handler
            log_dir = './logs'
            os.makedirs(log_dir, exist_ok=True)  # Ensure directory exists
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

        return logger

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)