import os
import nextcord
from nextcord.ext import commands
from core.utilities.logger import logger
from core.auth.decorators import admin_only, guest_only, respond_encrypted_file_in_dm
from modules.wireguard.utils import get_user_config


@commands.command(name='wireguard_get_qr_from_user')
@admin_only()
@respond_encrypted_file_in_dm()
async def wireguard_get_qr_from_user(ctx, username: str):
    """Sendet die WireGuard-Config eines bestimmten Users als QR-Code."""
    logger.debug(f"Executing get_user_qr command for user: {username}")
    config_path = "/app/bot/database/wireguard"
    
    user_config = get_user_config(config_path, username)
    
    if user_config:
        user_dir = os.path.join(config_path, f"peer_{username}")
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
@guest_only()
async def wireguard_qr(ctx):
    """Sendet dem Benutzer automatisch seinen WireGuard-QR-Code basierend auf dem Discord-Namen."""
    username = ctx.author.name  # Holt den Discord-Namen
    logger.debug(f"Executing auto_send_user_qr command for user: {username}")
    
    config_path = "/app/bot/database/wireguard"
    user_config = get_user_config(config_path, username)
    
    if user_config:
        user_dir = os.path.join(config_path, f"peer_{username}")
        qr_code_file = os.path.join(user_dir, f"peer_{username}.png")
        
        if os.path.exists(qr_code_file):
            logger.debug(f"Using existing QR code file: {qr_code_file}")
            return qr_code_file
        else:
            logger.warning(f"QR code file not found for user {username} at path: {qr_code_file}")
            return None
    else:
        return None
