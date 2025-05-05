from typing import Dict, Any, List
from dataclasses import dataclass, field
import logging
import logging.handlers # Import handlers module

@dataclass
class LoggingConfig:
    """Configuration for logging system"""
    # Format configuration
    format: str = "%(asctime)s [%(levelname).1s] %(message)s"  # Kürzeres Format mit Level als Buchstabe
    date_format: str = "%H:%M:%S"  # Nur Zeit, kein Datum
    
 
    console_level: str = "INFO"
    file_level: str = "INFO" # Keep for potential future use
    
    # Memory Handler configuration
    memory_capacity: int = 200 # How many log records to keep in memory
    memory_flush_level: int = logging.ERROR # Flush on ERROR or higher
    
    # File configuration (keep for potential future use)
    max_bytes: int = 1_000_000
    backup_count: int = 5
    
    # Database logging
    log_to_db: bool = False
    db_level: str = "WARNING"
    
    # Handlers - Ensure console is always present for MemoryHandler target
    handlers: List[str] = field(default_factory=lambda: ["console", "memory"]) # Add memory default
    
    def configure_logging(self) -> None:
        """Configure the root logger with the current settings"""
        root_logger = logging.getLogger()
        # Clear existing handlers first to prevent duplicates on reconfigure
        root_logger.handlers.clear()
        
        # --- MODIFICATION 1 & 4: Set root logger level directly to DEBUG ---
        # We set it to DEBUG so that all messages are processed and can reach handlers (like MemoryHandler)
        # Handlers themselves will filter based on their own configured levels.
        root_logger.setLevel(logging.DEBUG)

        configured_handlers: List[logging.Handler] = [] 

        # --- Setup Console Handler (always needed as target for memory) ---
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt=self.format, datefmt=self.date_format)
        console_handler.setFormatter(formatter)
        console_level_num = getattr(logging, self.console_level, logging.INFO)
        console_handler.setLevel(console_level_num)
        configured_handlers.append(console_handler)
        # No need to track min_level anymore

        # --- Setup Memory Handler (if requested) ---
        if "memory" in self.handlers:
            memory_handler = logging.handlers.MemoryHandler(
                capacity=self.memory_capacity,
                flushLevel=self.memory_flush_level, # Use the configured flush level (now ERROR)
                target=console_handler, # Target the console handler
                flushOnClose=True
            )
            # MemoryHandler doesn't have a level itself, it passes everything to target
            configured_handlers.append(memory_handler)
            # Note: The memory handler itself doesn't influence the root logger level directly

        # --- (Optional) Setup File Handler (if requested and needed later) ---
        # if "file" in self.handlers:
        #     log_dir = "logs"
        #     os.makedirs(log_dir, exist_ok=True)
        #     log_file = os.path.join(log_dir, "bot.log")
        #     file_handler = logging.handlers.RotatingFileHandler(
        #         log_file, maxBytes=self.max_bytes, backupCount=self.backup_count, encoding='utf-8'
        #     )
        #     file_handler.setFormatter(formatter) # Use the same formatter
        #     file_level_num = getattr(logging, self.file_level, logging.INFO)
        #     file_handler.setLevel(file_level_num)
        #     configured_handlers.append(file_handler)
        #     min_level = min(min_level, file_level_num)

        # Add all configured handlers to the root logger
        for handler in configured_handlers:
            root_logger.addHandler(handler)
            
        # --- MODIFICATION 5: Update final log message ---
        logging.info(f"Logging configured with handlers: {[h.__class__.__name__ for h in configured_handlers]}, root level: {logging.getLevelName(root_logger.level)}")
        
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