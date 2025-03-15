"""
Environment variable loader for web configuration
Uses shared env loader functionality
"""
import os
from app.shared.infrastructure.config.env_loader import (
    load_env_var, load_required_env_var, load_int_env_var, 
    load_bool_env_var, load_list_env_var, load_user_groups
)
from app.shared.logging import logger

def ensure_web_env_loaded() -> bool:
    """Ensure web environment variables are loaded"""
    try:
        # Set default values for web-specific variables if not set
        web_defaults = {
            "DISCORD_REDIRECT_URI": "http://localhost:8000/auth/callback",
            "JWT_SECRET_KEY": os.environ.get("JWT_SECRET_KEY", "fallback_development_secret_key_not_for_production"),
        }
        
        for key, default_value in web_defaults.items():
            if not os.getenv(key):
                os.environ[key] = default_value
                logger.debug(f"Using default value for {key}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to load web environment: {e}")
        return False

def get_discord_oauth_config() -> dict:
    """Get Discord OAuth configuration"""
    return {
        "client_id": load_env_var("DISCORD_BOT_ID", ""),
        "client_secret": load_env_var("DISCORD_BOT_SECRET", ""),
        "redirect_uri": load_env_var("DISCORD_REDIRECT_URI", "http://localhost:8000/auth/callback"),
        "api_endpoint": "https://discord.com/api/v10"
    }

def get_jwt_config() -> dict:
    """Get JWT configuration"""
    return {
        "secret_key": load_env_var("JWT_SECRET_KEY", "development_jwt_secret"),
        "algorithm": "HS256",
        "access_token_expire_minutes": load_int_env_var("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    } 