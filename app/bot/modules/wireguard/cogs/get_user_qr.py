import os
import nextcord
from nextcord.ext import commands
from core.utilities.logger import logger
from core.decorators.auth import admin_or_higher, user_or_higher
from core.decorators.respond import respond_encrypted_file_in_dm
from modules.wireguard.utils.get_user_config import get_user_config

class WireguardQRCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "/app/bot/database/wireguard"

    @commands.command(name='wireguard_get_qr_from_user')
    @admin_or_higher()
    @respond_encrypted_file_in_dm()
    async def wireguard_get_qr_from_user(self, ctx, username: str):
        """Sendet die WireGuard-Config eines bestimmten Users als QR-Code."""
        logger.debug(f"Executing get_user_qr command for user: {username}")
        
        user_config = get_user_config(self.config_path, username)
        
        if user_config:
            user_dir = os.path.join(self.config_path, f"peer_{username}")
            qr_code_file = os.path.join(user_dir, f"peer_{username}.png")
            
            if os.path.exists(qr_code_file):
                logger.debug(f"Using existing QR code file: {qr_code_file}")
                return qr_code_file
            else:
                logger.warning(f"QR code file not found for user {username} at path: {qr_code_file}")
                return None
        else:
            return None

    @commands.command(name='wireguard_qr')
    @respond_encrypted_file_in_dm()
    @user_or_higher()
    async def wireguard_qr(self, ctx):
        """Sendet dem Benutzer automatisch seinen WireGuard-QR-Code basierend auf dem Discord-Namen."""
        username = ctx.author.name  # Holt den Discord-Namen
        logger.debug(f"Executing auto_send_user_qr command for user: {username}")
        
        user_config = get_user_config(self.config_path, username)
        
        if user_config:
            user_dir = os.path.join(self.config_path, f"peer_{username}")
            qr_code_file = os.path.join(user_dir, f"peer_{username}.png")
            
            if os.path.exists(qr_code_file):
                logger.debug(f"Using existing QR code file: {qr_code_file}")
                return qr_code_file
            else:
                logger.warning(f"QR code file not found for user {username} at path: {qr_code_file}")
                return None
        else:
            return None

async def setup(bot):
    await bot.add_cog(WireguardQRCommands(bot))
