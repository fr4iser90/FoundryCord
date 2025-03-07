import os
from infrastructure.logging import logger

def get_user_config(config_path, username):
    user_dir = os.path.join(config_path, f"peer_{username}")
    config_file = os.path.join(user_dir, f"peer_{username}.conf")
    
    logger.debug(f"Checking user config at {config_file}")
    
    if not os.path.exists(config_file):
        logger.warning(f"Config file for {username} not found")
        return None

    with open(config_file, 'r') as f:
        return f.read().strip()
