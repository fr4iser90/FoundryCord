"""
Environment variable loader for configuration
Separates environment loading from domain models
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
    # Load environment variables
    super_admins_env = load_env_var('SUPER_ADMINS')
    admins_env = load_env_var('ADMINS')
    moderators_env = load_env_var('MODERATORS')
    users_env = load_env_var('USERS')
    guests_env = load_env_var('GUESTS')
    
    # Parse into dictionaries
    return {
        'super_admins': parse_users(super_admins_env),
        'admins': parse_users(admins_env),
        'moderators': parse_users(moderators_env),
        'users': parse_users(users_env),
        'guests': parse_users(guests_env)
    }
