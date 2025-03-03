# app/bot/modules/wireguard/__init__.py

from .cogs.get_user_config import WireguardConfigCommands
from .cogs.get_user_qr import WireguardQRCommands
from .utils.get_user_config import get_user_config

def setup(bot):
    bot.add_cog(WireguardConfigCommands(bot))
    bot.add_cog(WireguardQRCommands(bot))

__all__ = ["WireguardConfigCommands", "WireguardQRCommands", "get_user_config", "setup"]
