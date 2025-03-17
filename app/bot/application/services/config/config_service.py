"""Configuration service for bot configuration management."""
from typing import Dict, Any, Optional
import os
import json
import yaml
from pathlib import Path

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class ConfigService:
    """Service for managing bot configuration."""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize the configuration service."""
        try:
            # Load configuration from environment variables
            self._load_from_env()
            
            # Load configuration from files
            await self._load_from_files()
            
            # Set bot.config reference
            self.bot.config = self
            
            self.initialized = True
            logger.info("Configuration service initialized")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing configuration service: {e}")
            return False
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Look for variables with BOT_CONFIG_ prefix
        for key, value in os.environ.items():
            if key.startswith("BOT_CONFIG_"):
                config_key = key[11:].lower()  # Remove prefix and convert to lowercase
                
                # Try to convert to appropriate type
                if value.lower() == "true":
                    self.config[config_key] = True
                elif value.lower() == "false":
                    self.config[config_key] = False
                elif value.isdigit():
                    self.config[config_key] = int(value)
                elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                    self.config[config_key] = float(value)
                else:
                    self.config[config_key] = value
                    
        logger.info(f"Loaded {len(self.config)} configuration values from environment variables")
    
    async def _load_from_files(self):
        """Load configuration from files."""
        try:
            # Try to load configuration from YAML
            config_path = Path("config/bot_config.yaml")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config:
                        self.config.update(yaml_config)
                        logger.info(f"Loaded configuration from {config_path}")
            
            # Try to load configuration from JSON
            config_path = Path("config/bot_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    json_config = json.load(f)
                    if json_config:
                        self.config.update(json_config)
                        logger.info(f"Loaded configuration from {config_path}")
                    
        except Exception as e:
            logger.error(f"Error loading configuration from files: {e}")
    
    def get(self, key, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value."""
        self.config[key] = value
        return True
    
    def __getitem__(self, key):
        """Get a configuration value using dictionary syntax."""
        return self.config.get(key)
    
    def __setitem__(self, key, value):
        """Set a configuration value using dictionary syntax."""
        self.config[key] = value 