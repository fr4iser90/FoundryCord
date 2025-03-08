import os
import nextcord
from typing import Dict
from infrastructure.logging import logger

class EnvConfig:
    def __init__(self):
        self.environment = None
        self.is_development = False
        self.is_production = False
        self.discord_token = None
        self.guild_id = None
        self.HOMELAB_CATEGORY_ID= None
        self.user_groups = {}

    def load(self) -> None:
        """Load all environment variables"""
        try:
            # Load basic environment settings
            self.environment = os.getenv('ENVIRONMENT', 'production').lower()
            self.is_development = self.environment == 'development'
            self.is_production = self.environment == 'production'
            
            # Load required variables
            self.discord_token = self.load_required_env_var('DISCORD_TOKEN')
            self.guild_id = self.load_int_env_var('DISCORD_SERVER')
            self.HOMELAB_CATEGORY_ID = self.load_int_env_var('HOMELAB_CATEGORY_ID')
            
            # Load user groups
            self.user_groups = self._load_user_groups()
            
            logger.info(f"Environment configuration loaded successfully: {self.environment}")
        except Exception as e:
            logger.error(f"Failed to load environment configuration: {e}")
            raise

    def get_intents(self) -> nextcord.Intents:
        intents = nextcord.Intents.default()
        intents.messages = True
        intents.guilds = True
        intents.members = True
        intents.message_content = True
        intents.dm_messages = True
        intents.guild_messages = True
        intents.dm_reactions = True
        return intents
    
    @staticmethod
    def load_env_var(name: str, default: str = '') -> str:
        """Load an environment variable with default value"""
        value = os.getenv(name, default)
        return value

    @staticmethod
    def load_required_env_var(name: str) -> str:
        value = os.getenv(name)
        if value is None:
            raise ValueError(f"Required environment variable '{name}' is not set")
        return value

    @staticmethod
    def load_int_env_var(name: str, default: int = 0) -> int:
        value = os.getenv(name)
        return int(value) if value else default
    
    def _load_user_groups(self) -> Dict[str, Dict[str, str]]:
        """Load all user groups from environment variables"""
        groups = ['SUPER_ADMINS', 'ADMINS', 'MODERATORS', 'USERS', 'GUESTS']
        return {
            group.lower(): self._parse_users(os.getenv(group, ''))
            for group in groups
        }

    @staticmethod
    def _parse_users(users_str: str) -> Dict[str, str]:
        """Parse user string format into dictionary"""
        users_dict = {}
        if users_str:
            for user_entry in users_str.split(','):
                if '|' in user_entry:
                    username, user_id = user_entry.split('|')
                    users_dict[username.strip()] = user_id.strip()
        return users_dict
    

