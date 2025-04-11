"""
Wireguard configuration manager
Handles VPN configuration management
"""
import os
from typing import Optional, Dict, Any
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class WireguardConfigManager:
    """Manages Wireguard VPN configurations"""
    
    def __init__(self):
        """Initialize the config manager"""
        self.config_path = "/etc/wireguard"
    
    def get_user_config(self, base_path: str, username: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a user"""
        config_file = self.get_config_file_path(base_path, username)
        if not os.path.exists(config_file):
            return None
            
        try:
            with open(config_file, 'r') as f:
                return {"config": f.read()}
        except Exception as e:
            logger.error(f"Error reading config for {username}: {e}")
            return None
    
    def get_config_file_path(self, base_path: str, username: str) -> str:
        """Get the configuration file path for a user"""
        return os.path.join(base_path, f"{username}.conf")
    
    def get_qr_file_path(self, base_path: str, username: str) -> str:
        """Get the QR code file path for a user"""
        return os.path.join(base_path, f"{username}.png") 