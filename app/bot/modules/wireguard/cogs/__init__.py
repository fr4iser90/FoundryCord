# app/bot/modules/wireguard/cogs/__init__.py

from .get_user_config import WireguardConfigCommands
from .get_user_qr import WireguardQRCommands

__all__ = ["WireguardConfigCommands", "WireguardQRCommands"]
