# app/bot/modules/wireguard/__init__.py

from core.utilities.logger import logger
from .cogs.get_user_config import WireguardConfigCommands
from .cogs.get_user_qr import WireguardQRCommands

async def setup(bot):
    """Setup function for the wireguard module"""
    try:
        # Initialize both cogs
        config_cog = WireguardConfigCommands(bot)
        qr_cog = WireguardQRCommands(bot)
        
        # Add cogs to bot
        bot.add_cog(config_cog)
        bot.add_cog(qr_cog)
        
        logger.info("Wireguard commands initialized successfully")
        return config_cog  # Return primary cog
    except Exception as e:
        logger.error(f"Failed to initialize wireguard: {e}")
        raise

__all__ = ["WireguardConfigCommands", "WireguardQRCommands"]
