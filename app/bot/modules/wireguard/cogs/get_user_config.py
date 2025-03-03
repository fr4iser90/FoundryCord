import os
import nextcord
from nextcord.ext import commands
from core.utilities.logger import logger
from core.decorators.auth import admin_or_higher, user_or_higher
from core.decorators.respond import (
    respond_in_channel,
    respond_using_config,
    respond_in_dm,
    respond_encrypted_in_dm,
    respond_with_file,
    respond_encrypted_file_in_dm
)
from modules.wireguard.utils.get_user_config import get_user_config

class WireguardConfigCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "/app/bot/database/wireguard"

    @commands.command(name='wireguard_get_config_from_user')
    @admin_or_higher()
    @respond_encrypted_file_in_dm()
    async def wireguard_get_config_from_user(self, ctx, username: str):
        """Gibt die Konfigurationsdatei eines bestimmten WireGuard-Users zurück."""
        logger.debug(f"Executing get_user_config command for user: {username}")
        
        user_config = get_user_config(self.config_path, username)
        
        if user_config:
            user_dir = os.path.join(self.config_path, f"peer_{username}")
            config_file = os.path.join(user_dir, f"peer_{username}.conf")
            
            if os.path.exists(config_file):
                logger.debug(f"Using existing config file: {config_file}")
                return config_file
            else:
                logger.warning(f"Config file not found for user {username} at path: {config_file}")
                return None
        else:
            return None

    @commands.command(name='wireguard_config')
    @user_or_higher()
    @respond_encrypted_file_in_dm()
    async def wireguard_config(self, ctx):
        """Sendet dem Benutzer automatisch das wireguard conf file basierend auf dem Discord-Namen."""
        username = ctx.author.name  # Holt den Discord-Namen
        logger.debug(f"Executing auto_send_user_qr command for user: {username}")
        
        user_config = get_user_config(self.config_path, username)
        
        if user_config:
            user_dir = os.path.join(self.config_path, f"peer_{username}")
            config_file = os.path.join(user_dir, f"peer_{username}.conf")
            
            if os.path.exists(config_file):
                logger.debug(f"Using existing config file: {config_file}")
                return config_file
            else:
                logger.warning(f"Config file not found for user {username} at path: {config_file}")
                return None
        else:
            return None

async def setup(bot):
    await bot.add_cog(WireguardConfigCommands(bot))
