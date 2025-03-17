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
        # Basic Discord configuration
        self.config['DISCORD_TOKEN'] = os.getenv('DISCORD_TOKEN')
        self.config['DISCORD_GUILD_ID'] = os.getenv('DISCORD_GUILD_ID')
        self.config['DISCORD_CLIENT_ID'] = os.getenv('DISCORD_CLIENT_ID')
        self.config['DISCORD_CLIENT_SECRET'] = os.getenv('DISCORD_CLIENT_SECRET')
        
        # Database configuration
        self.config['POSTGRES_USER'] = os.getenv('APP_DB_USER', 'homelab_discord_bot')
        self.config['POSTGRES_PASSWORD'] = os.getenv('APP_DB_PASSWORD')
        self.config['POSTGRES_HOST'] = os.getenv('POSTGRES_HOST', 'homelab-postgres')
        self.config['POSTGRES_PORT'] = os.getenv('POSTGRES_PORT', '5432')
        self.config['POSTGRES_DB'] = os.getenv('POSTGRES_DB', 'homelab')
        
        # Environment configuration
        self.config['ENVIRONMENT'] = os.getenv('ENVIRONMENT', 'development')
        self.config['LOG_LEVEL'] = os.getenv('LOG_LEVEL', 'INFO')
        
        # Security keys
        self.config['AES_KEY'] = os.getenv('AES_KEY')
        self.config['ENCRYPTION_KEY'] = os.getenv('ENCRYPTION_KEY')
        self.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
        
        logger.debug("Loaded configuration from environment variables")
    
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