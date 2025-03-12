"""
Environment variable loader for configuration
Separates environment loading from app.bot.domain models
"""
import os
from typing import Dict

def load_env_var(name: str, default: str = '') -> str:
    """Load an environment variable with default value"""
    return os.getenv(name, default)

def parse_users(users_str: str) -> Dict[str, str]:
    """Parse user string format into dictionary of username -> user_id"""
    users_dict = {}
    if users_str:
        for user_entry in users_str.split(','):
            if '|' in user_entry:
                username, user_id = user_entry.split('|')
                users_dict[username.strip()] = user_id.strip()
    return users_dict

def load_user_groups() -> Dict[str, Dict[str, str]]:
    """Load all user groups from environment variables"""
    from app.bot.infrastructure.config.constants.role_constants import DEFAULT_USER_GROUPS
    
    # Start with default empty groups
    result = DEFAULT_USER_GROUPS.copy()
    
    # Parse user groups from environment
    for group_name in DEFAULT_USER_GROUPS.keys():
        env_name = group_name.upper().replace('_', '')  # super_admins -> SUPERADMINS
        env_value = os.environ.get(env_name, '')
        
        if env_value:
            result[group_name] = parse_users(env_value)
    
    return result

def load_typed_env_var(name: str, var_type, default=None):
    """Lädt eine Umgebungsvariable und konvertiert sie in den angegebenen Typ"""
    value = os.getenv(name)
    if value is None:
        return default
        
    if var_type == bool:
        return value.lower() in ('true', 'yes', '1', 'y')
    return var_type(value)

def load_int_env_var(name: str, default: int = 0) -> int:
    """Lädt eine Umgebungsvariable als Integer"""
    return load_typed_env_var(name, int, default)

def load_bool_env_var(name: str, default: bool = False) -> bool:
    """Lädt eine Umgebungsvariable als Boolean"""
    return load_typed_env_var(name, bool, default)

def load_list_env_var(name: str, separator: str = ',', default: list = None) -> list:
    """Lädt eine durch Separator getrennte Umgebungsvariable als Liste"""
    value = os.getenv(name, '')
    if not value and default is not None:
        return default
    return [item.strip() for item in value.split(separator) if item.strip()]

def load_required_env_var(name: str) -> str:
    """Lädt eine obligatorische Umgebungsvariable oder wirft einen Fehler"""
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Required environment variable '{name}' is not set")
    return value

def get_channel_config():
    """Lädt die für Channel-Setup relevanten Umgebungsvariablen"""
    return {
        'server_id': load_int_env_var('DISCORD_SERVER'),
        'HOMELAB_CATEGORY_ID': load_int_env_var('HOMELAB_CATEGORY_ID'),
    }
