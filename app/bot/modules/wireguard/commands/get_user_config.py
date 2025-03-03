import os
import nextcord
from nextcord.ext import commands
from core.utilities.logger import logger
from core.decorators.auth import admin_only, guest_only
from core.decorators.respond import respond_in_channel, respond_using_config, respond_in_dm, respond_encrypted_in_dm, respond_with_file, respond_encrypted_file_in_dm 
from modules.wireguard.utils import get_user_config

@commands.command(name='wireguard_get_config_from_user')
@admin_only()
@respond_encrypted_file_in_dm()
async def wireguard_get_config_from_user(ctx, username: str):
    """Gibt die Konfigurationsdatei eines bestimmten WireGuard-Users zurück."""
    logger.debug(f"Executing get_user_config command for user: {username}")
    config_path = "/app/bot/database/wireguard"
    
    user_config = get_user_config(config_path, username)
    
    if user_config:
        user_dir = os.path.join(config_path, f"peer_{username}")
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
@respond_encrypted_file_in_dm()
@guest_only()
async def wireguard_config(ctx):
    """Sendet dem Benutzer automatisch das wireguard conf file basierend auf dem Discord-Namen."""
    username = ctx.author.name  # Holt den Discord-Namen
    logger.debug(f"Executing auto_send_user_qr command for user: {username}")
    
    config_path = "/app/bot/database/wireguard"
    user_config = get_user_config(config_path, username)
    
    if user_config:
        user_dir = os.path.join(config_path, f"peer_{username}")
        config_file = os.path.join(user_dir, f"peer_{username}.conf")
        
        if os.path.exists(config_file):
            logger.debug(f"Using existing config file: {config_file}")
            return config_file
        else:
            logger.warning(f"Config file not found for user {username} at path: {config_file}")
            return None
    else:
        return None
