"""Collector for basic bot information."""
from typing import Dict, Any
import time
import sys
import nextcord

# Note: No logger import here, assumes logging is handled by the calling class if needed

def collect_basic_info_func(bot: nextcord.Client) -> Dict[str, Any]:
    """
    Collects basic bot information from the bot instance.
    
    Args:
        bot: The Discord bot instance.
        
    Returns:
        Dict with basic bot information.
    """
    if not bot:
        return {"error": "Bot instance not provided"}
        
    return {
        "uptime": time.time() - bot.start_time if hasattr(bot, 'start_time') else None,
        "version": getattr(bot, 'version', 'unknown'),
        "nextcord_version": nextcord.__version__,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment": getattr(bot, 'env_config', {}).get('environment', 'unknown'),
        "is_development": getattr(bot, 'env_config', {}).get('is_development', False),
        "lifecycle_state": bot.lifecycle.get_state() if hasattr(bot, 'lifecycle') else 'unknown'
    } 