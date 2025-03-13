import os
import nextcord
import secrets
import base64
from cryptography.fernet import Fernet
from typing import Dict
from app.shared.logging import logger

class EnvConfig:
    def __init__(self):
        self.environment = None
        self.is_development = False
        self.is_production = False
        self.discord_token = None
        self.guild_id = None
        self.HOMELAB_CATEGORY_ID = None
        self.user_groups = {}


    def _ensure_secure_keys(self):
        """Ensure all security keys are set, generating if needed"""
        # Check AES_KEY
        if not os.getenv('AES_KEY'):
            generated_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
            os.environ['AES_KEY'] = generated_key
            logger.warning(f"Generated missing AES_KEY: {generated_key[:5]}...")
            
        # Check ENCRYPTION_KEY  
        if not os.getenv('ENCRYPTION_KEY'):
            generated_key = Fernet.generate_key().decode()
            os.environ['ENCRYPTION_KEY'] = generated_key
            logger.warning(f"Generated missing ENCRYPTION_KEY: {generated_key[:5]}...")
            
        # Check JWT_SECRET_KEY
        if not os.getenv('JWT_SECRET_KEY'):
            generated_key = base64.urlsafe_b64encode(os.urandom(24)).decode()
            os.environ['JWT_SECRET_KEY'] = generated_key
            logger.warning(f"Generated missing JWT_SECRET_KEY: {generated_key[:5]}...")

    def load(self) -> None:
        """Load all environment variables with smart defaults"""
        try:
            # Load basic environment settings
            self.environment = os.getenv('ENVIRONMENT', 'development').lower()
            self.is_development = self.environment == 'development'
            self.is_production = self.environment == 'production'
            
            # Load required variables
            self.discord_token = self.load_required_env_var('DISCORD_TOKEN')
            self.guild_id = self.load_int_env_var('DISCORD_SERVER')
            
            # HOMELAB_CATEGORY_ID is now optional with special handling
            category_id = os.getenv('HOMELAB_CATEGORY_ID', 'auto')
            self.HOMELAB_CATEGORY_ID = int(category_id) if category_id.isdigit() else None
            
            # Load user groups
            self.user_groups = self._load_user_groups()
            
            # Fill in missing optional values with defaults
            self._load_defaults()
            
            logger.info(f"Environment configuration loaded successfully: {self.environment}")
        except Exception as e:
            logger.error(f"Failed to load environment configuration: {e}")
            raise
            
    def _load_defaults(self):
        """Apply default values to missing optional variables"""
        # Define default values for optional variables
        defaults = {
            "DOMAIN": "localhost",
            "TYPE": "Web,Game,File",
            "SESSION_DURATION_HOURS": "24",
            "RATE_LIMIT_WINDOW": "60",
            "RATE_LIMIT_MAX_ATTEMPTS": "5",
            "PUID": "1001",
            "PGID": "987",
        }
        
        # Apply defaults if variables aren't set
        for key, default_value in defaults.items():
            if not os.getenv(key):
                os.environ[key] = default_value
                logger.debug(f"Using default value for {key}: {default_value}")

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
    

