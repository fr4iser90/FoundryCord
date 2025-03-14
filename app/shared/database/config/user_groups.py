"""User role groups loaded from environment variables"""
import os

def parse_users(user_str):
    """Parse user string into dictionary of username:discord_id pairs"""
    if not user_str:
        return {}
    
    users_dict = {}
    for user_entry in user_str.split(','):
        if '|' in user_entry:
            username, user_id = user_entry.split('|', 1)
            users_dict[username.strip()] = user_id.strip()
    return users_dict

def load_user_groups():
    """Load all user groups from environment variables"""
    # Load environment variables
    super_admins_env = os.environ.get('SUPER_ADMINS', '')
    admins_env = os.environ.get('ADMINS', '')
    moderators_env = os.environ.get('MODERATORS', '')
    users_env = os.environ.get('USERS', '')
    guests_env = os.environ.get('GUESTS', '')
    
    # Parse into dictionaries
    return {
        'super_admins': parse_users(super_admins_env),
        'admins': parse_users(admins_env),
        'moderators': parse_users(moderators_env),
        'users': parse_users(users_env),
        'guests': parse_users(guests_env)
    }
