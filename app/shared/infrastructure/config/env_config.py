import os
import logging
import nextcord
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class EnvConfig:
    """
    Environment configuration for the application.
    Handles loading and validation of environment variables.
    """
    
    def __init__(self):
        self.environment = None
        self.DISCORD_BOT_TOKEN = None
        self.guild_id = None
        
    def load(self):
        """Load all environment variables"""
        try:
            # Load required application variables
            self.DISCORD_BOT_TOKEN = self._load_required_env_var('DISCORD_BOT_TOKEN')

            
            logger.info("Environment configuration loaded successfully")
            return self
            
        except Exception as e:
            logger.error(f"Failed to load environment configuration: {e}")
            raise
    
    def get_intents(self):
        """Return Discord intents for the bot"""
        intents = nextcord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.presences = True
        return intents
    
    @staticmethod
    def _load_required_env_var(name):
        """Load a required environment variable"""
        value = os.getenv(name)
        if value is None:
            raise ValueError(f"Required environment variable '{name}' is not set")
        return value
        
    @staticmethod
    def _load_int_env_var(name):
        """Load an environment variable as an integer"""
        value = os.getenv(name)
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Environment variable '{name}' must be an integer")
