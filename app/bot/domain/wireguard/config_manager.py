import os
from app.bot.infrastructure.logging import logger

class WireguardConfigManager:
    """Domain logic for managing WireGuard configurations"""
    
    @staticmethod
    def get_user_config(config_path, username):
        """Get a user's WireGuard configuration"""
        user_dir = os.path.join(config_path, f"peer_{username}")
        config_file = os.path.join(user_dir, f"peer_{username}.conf")
        
        logger.debug(f"Checking user config at {config_file}")
        
        if not os.path.exists(config_file):
            logger.warning(f"Config file for {username} not found")
            return None

        with open(config_file, 'r') as f:
            return f.read().strip()
    
    @staticmethod
    def get_config_file_path(config_path, username):
        """Get the path to a user's configuration file"""
        user_dir = os.path.join(config_path, f"peer_{username}")
        return os.path.join(user_dir, f"peer_{username}.conf")
    
    @staticmethod
    def get_qr_file_path(config_path, username):
        """Get the path to a user's QR code file"""
        user_dir = os.path.join(config_path, f"peer_{username}")
        return os.path.join(user_dir, f"peer_{username}.png")