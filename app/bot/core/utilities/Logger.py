import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import json

# Base Logger class
class CoreLogger:
    def __init__(self, name, log_level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # Define formatter
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Setup console handler
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(logging.DEBUG)
        self.console_handler.setFormatter(self.formatter)

        # Setup file handler with rotating
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        self.file_handler = RotatingFileHandler(
            os.path.join(log_dir, f'{name}.log'),
            maxBytes=10**6,  # 1 MB log size
            backupCount=5
        )
        self.file_handler.setLevel(logging.INFO)
        self.file_handler.setFormatter(self.formatter)

        # Add handlers
        self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.file_handler)

    def set_log_level(self, level):
        """Method to dynamically adjust the logging level"""
        self.logger.setLevel(level)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

# ModuleLogger adds module-specific features
class ModuleLogger(CoreLogger):
    def __init__(self, module_name):
        super().__init__(f'homelab_bot.{module_name}')

    def module_specific_log(self, action, details):
        """Custom logging method for module-specific events"""
        self.info(f"[{action}] {details}")

    def log_error_and_notify(self, error_message):
        """Module-specific method to log error and notify admins (e.g., email or external service)"""
        self.error(error_message)
        # Example: send email or notify service
        # self.notify_admins(error_message)

# LoggerContext class to add context dynamically
class LoggerContextAdapter(logging.LoggerAdapter):
    def __init__(self, logger, extra):
        super().__init__(logger, extra)
    
    def process(self, msg, kwargs):
        return f"{self.extra} - {msg}", kwargs

# Example of adding context
context_info = {'module': 'wireguard', 'user': 'admin'}
main_logger = CoreLogger('homelab_bot')
main_logger_with_context = LoggerContextAdapter(main_logger.logger, context_info)
main_logger_with_context.info("System started")

# # Module logger usage example
# wireguard_logger = ModuleLogger('wireguard')
# wireguard_logger.module_specific_log('CONNECTION', 'User connected')
# wireguard_logger.log_error_and_notify('Wireguard failed to connect!')

# # Dynamically change log level
# main_logger.set_log_level(logging.WARNING)
# main_logger.debug("This will not be shown at WARNING level")
# main_logger.warning("This will be shown")
How could we improve this? to have a better workflow for everyt thing and logger etc?
