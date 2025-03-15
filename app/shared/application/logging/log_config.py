from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class LoggingConfig:
    """Configuration for logging system"""
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%d-%m %H:%M:%S"
    console_level: str = "INFO"
    file_level: str = "INFO"
    debug_level: str = "DEBUG"
    max_bytes: int = 1_000_000
    backup_count: int = 5
    log_to_db: bool = False
    db_level: str = "WARNING"
    handlers: List[str] = field(default_factory=lambda: ["console", "file"])
    
    def update(self, config: Dict[str, Any]) -> None:
        """Update configuration with provided values"""
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)

# Global configuration instance
config = LoggingConfig()

def get_config() -> LoggingConfig:
    """Get the current logging configuration"""
    return config

def update_config(new_config: Dict[str, Any]) -> None:
    """Update the global logging configuration"""
    config.update(new_config)