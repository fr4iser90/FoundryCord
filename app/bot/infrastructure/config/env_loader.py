"""
Environment variable loader for bot configuration
Uses shared env loader functionality
"""

from app.shared.infrastructure.config.env_loader import (
    load_env_var, load_required_env_var, load_int_env_var, 
    load_bool_env_var, load_list_env_var, load_user_groups, 
    parse_users, load_typed_env_var
)
from app.bot.infrastructure.config.constants.role_constants import DEFAULT_USER_GROUPS

def load_user_groups_with_defaults() -> dict:
    """Load all user groups from environment variables with defaults"""
    # Start with default empty groups
    result = DEFAULT_USER_GROUPS.copy()
    
    # Load user groups from environment
    user_groups = load_user_groups(DEFAULT_USER_GROUPS.keys())
    
    # Merge loaded groups with defaults
    for group_name, users in user_groups.items():
        if users:
            result[group_name] = users
    
    return result

def get_channel_config():
    """Load channel setup relevant environment variables"""
    return {
        'server_id': load_int_env_var('DISCORD_SERVER'),
        'HOMELAB_CATEGORY_ID': load_int_env_var('HOMELAB_CATEGORY_ID'),
    }
