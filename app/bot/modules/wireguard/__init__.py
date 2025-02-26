from .commands.get_user_config import wireguard_get_config_from_user, wireguard_config
from .commands.get_user_qr import wireguard_get_qr_from_user, wireguard_qr

def setup(bot):
    bot.add_command(wireguard_get_config_from_user)
    bot.add_command(wireguard_config)
    bot.add_command(wireguard_get_qr_from_user)
    bot.add_command(wireguard_qr)
