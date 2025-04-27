"""Collector for cog and extension status."""
from typing import Dict, Any
import nextcord
from app.shared.interface.logging.api import get_shared_logger

logger = get_shared_logger()

def collect_cog_status_func(bot: nextcord.Client) -> Dict[str, Any]:
    """
    Collects the status of loaded cogs and extensions from the bot instance.

    Args:
        bot: The Discord bot instance.

    Returns:
        Dict with cog/extension status information.
    """
    logger.debug("Executing cog_status state collector...")
    if not bot:
        return {"error": "Bot instance not provided"}
        
    try:
        cogs = bot.cogs
        extensions = list(bot.extensions.keys()) if hasattr(bot, 'extensions') else []
            
        # Get cog names safely
        cog_names = list(cogs.keys()) if cogs else []
            
        return {
            "loaded_cogs": sorted(cog_names),
            "cog_count": len(cog_names),
            "loaded_extensions": sorted(extensions),
            "extension_count": len(extensions)
        }
    except Exception as e:
        logger.error(f"Error collecting cog status: {e}", exc_info=True)
        return {"error": str(e)} 