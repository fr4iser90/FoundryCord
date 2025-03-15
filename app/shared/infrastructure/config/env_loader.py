"""
Shared environment variable loader for configuration
Provides consistent environment loading across bot and web components
"""
import os
from typing import Dict, List, Any, Optional

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

def load_typed_env_var(name: str, var_type: Any, default: Any = None) -> Any:
    """Load an environment variable and convert it to the specified type"""
    value = os.getenv(name)
    if value is None:
        return default
        
    if var_type == bool:
        return value.lower() in ('true', 'yes', '1', 'y')
    return var_type(value)

def load_int_env_var(name: str, default: int = 0) -> int:
    """Load an environment variable as integer"""
    return load_typed_env_var(name, int, default)

def load_bool_env_var(name: str, default: bool = False) -> bool:
    """Load an environment variable as boolean"""
    return load_typed_env_var(name, bool, default)

def load_list_env_var(name: str, separator: str = ',', default: Optional[List[str]] = None) -> List[str]:
    """Load a separator-delimited environment variable as list"""
    value = os.getenv(name, '')
    if not value and default is not None:
        return default
    return [item.strip() for item in value.split(separator) if item.strip()]

def load_required_env_var(name: str) -> str:
    """Load a required environment variable or throw an error"""
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Required environment variable '{name}' is not set")
    return value

def load_user_groups(group_names: List[str]) -> Dict[str, Dict[str, str]]:
    """Load user groups from environment variables"""
    result = {group_name.lower(): {} for group_name in group_names}
    
    # Parse user groups from environment
    for group_name in group_names:
        env_name = group_name.upper().replace('_', '')  # super_admins -> SUPERADMINS
        env_value = os.environ.get(env_name, '')
        
        if env_value:
            result[group_name.lower()] = parse_users(env_value) 