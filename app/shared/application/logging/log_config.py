from typing import Dict, Any, List
from dataclasses import dataclass, field
import logging
from app.shared.application.logging.formatters import CompactFormatter

@dataclass
class LoggingConfig:
    """Configuration for logging system"""
    # Format configuration
    format: str = "%(asctime)s [%(levelname).1s] %(message)s"  # Kürzeres Format mit Level als Buchstabe
    date_format: str = "%H:%M:%S"  # Nur Zeit, kein Datum
    
    # Level configuration
    console_level: str = "INFO"
    file_level: str = "INFO"
    debug_level: str = "DEBUG"
    
    # File configuration
    max_bytes: int = 1_000_000
    backup_count: int = 5
    
    # Database logging
    log_to_db: bool = False
    db_level: str = "WARNING"
    
    # Handlers
    handlers: List[str] = field(default_factory=lambda: ["console", "file"])
    
    def configure_logging(self) -> None:
        """Configure the root logger with the current settings"""
        # Create console handler with compact formatter
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(CompactFormatter(datefmt=self.date_format))
        console_handler.setLevel(getattr(logging, self.console_level))
        
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Add configured handlers
        root_logger.addHandler(console_handler)
        root_logger.setLevel(getattr(logging, self.console_level))
    
    def update(self, config: Dict[str, Any]) -> None:
        """Update configuration with provided values"""
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
        # Reconfigure logging after update
        self.configure_logging()

# Global configuration instance
config = LoggingConfig()

def get_config() -> LoggingConfig:
    """Get the current logging configuration"""
    return config

def update_config(new_config: Dict[str, Any]) -> None:
    """Update the global logging configuration"""
    config.update(new_config)