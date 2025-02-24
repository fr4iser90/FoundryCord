import os
import nextcord
from nextcord.ext import commands
from modules.utilities.logger import logger
from modules.wireguard.utils import get_user_config
from modules.auth.decorators import admin_only, guest_only, respond_in_dm_in_codeblock


@commands.command(name='wireguard_get_qr_from_user')
@admin_only()
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
            await ctx.author.send(file=nextcord.File(qr_code_file))
        else:
            logger.warning(f"QR code file not found for user {username} at path: {qr_code_file}")
            await ctx.author.send(f"Keine QR-Code-Datei für den Benutzer '{username}' gefunden.")
    else:
        await ctx.author.send(f"Keine Konfiguration für den Benutzer '{username}' gefunden.")


@commands.command(name='wireguard_qr')
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
            await ctx.author.send(file=nextcord.File(qr_code_file))
        else:
            logger.warning(f"QR code file not found for user {username} at path: {qr_code_file}")
            await ctx.author.send(f"Keine QR-Code-Datei für den Benutzer '{username}' gefunden.")
    else:
        await ctx.author.send(f"Keine Konfiguration für den Benutzer '{username}' gefunden.")
