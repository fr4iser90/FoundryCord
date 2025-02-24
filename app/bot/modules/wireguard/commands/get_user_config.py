import os
import nextcord
from nextcord.ext import commands
from modules.utilities.logger import logger
from modules.wireguard.utils import get_user_config
from modules.auth.decorators import admin_only, guest_only, respond_in_dm_in_codeblock


@commands.command(name='wireguard_get_config_from_user')
@admin_only()
@respond_in_dm_in_codeblock()
async def wireguard_get_config_from_user(ctx, username: str):
    """Gibt die Konfigurationsdatei eines bestimmten WireGuard-Users zurück."""
    logger.debug(f"Executing get_user_config command for user: {username}")
    config_path = "/app/bot/database/wireguard"
    
    user_config = get_user_config(config_path, username)
    
    if user_config:
        logger.debug(f"Returning config content for user {username}")
        return user_config.strip()
    else:
        logger.warning(f"No config found for user: {username}")
        return f"Keine Konfiguration für den Benutzer '{username}' gefunden."
    

@commands.command(name='wireguard_config')
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
            await ctx.author.send(file=nextcord.File(config_file))
        else:
            logger.warning(f"Config file not found for user {username} at path: {config_file}")
            await ctx.author.send(f"Keine Config-Datei für den Benutzer '{username}' gefunden.")
    else:
        await ctx.author.send(f"Keine Konfiguration für den Benutzer '{username}' gefunden.")
