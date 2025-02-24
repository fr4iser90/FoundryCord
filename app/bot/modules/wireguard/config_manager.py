import psutil
import requests
from nextcord.ext import commands
import socket
import nextcord
from dotenv import load_dotenv
import os
import subprocess
import qrcode
from modules.utilities.logger import logger
from modules.auth.decorators import admin_only, respond_in_dm, respond_in_dm_in_codeblock

# Load environment variables from .env file
load_dotenv()

# Get DOMAIN from environment variable
DOMAIN = os.getenv('DOMAIN')

# Check if DOMAIN is loaded correctly
if not DOMAIN:
    logger.warning("DOMAIN not found in environment variables. Please check your .env file.")

def get_user_config(config_path, username):
    # Use new directory structure
    user_dir = os.path.join(config_path, f"peer_{username}")
    config_file = os.path.join(user_dir, f"peer_{username}.conf")
    
    # Debug: Print the expected directory and file paths
    logger.debug(f"Expected user directory: {user_dir}")
    logger.debug(f"Expected config file: {config_file}")
    
    # Debug: List contents of the user directory
    if os.path.exists(user_dir):
        logger.debug(f"Contents of {user_dir}: {os.listdir(user_dir)}")
    else:
        logger.warning(f"User directory not found: {user_dir}")
    
    if not os.path.exists(config_file):
        logger.warning(f"Config file not found for user {username} at path: {config_file}")
        return None
    
    with open(config_file, 'r') as f:
        config_content = f.read()
    
    # Debug: Print the content of the config file
    logger.debug(f"Config content for {username}:\n{config_content}")
    return config_content

def setup(bot):
    logger.info(f"Setting up wireguard_config command (Bot ID: {id(bot)})")
    
    @bot.command(name='wireguard_config')
    @admin_only()
    @respond_in_dm_in_codeblock()
    async def wireguard_config(ctx):
        logger.debug("Executing wireguard_config command")
        config_path = "/app/bot/database/wireguard/wg_confs"
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_content = f.read()
            
            logger.debug(f"Returning config content (Length: {len(config_content)} chars)")
            return config_content.strip()
        else:
            logger.warning(f"Config file not found at path: {config_path}")
            return "Die WireGuard-Konfigurationsdatei konnte nicht gefunden werden."

    @bot.command(name='wireguard_user_config')
    @admin_only()
    @respond_in_dm_in_codeblock()
    async def wireguard_user_config(ctx, username: str):
        logger.debug(f"Executing wireguard_user_config command for user: {username}")
        config_path = "/app/bot/database/wireguard"
        
        user_config = get_user_config(config_path, username)
        
        if user_config:
            logger.debug(f"Returning config content for user {username}")
            return user_config.strip()
        else:
            logger.warning(f"No config found for user: {username}")
            return f"Keine Konfiguration für den Benutzer '{username}' gefunden."

    @bot.command(name='wireguard_user_config_qr')
    @admin_only()
    async def wireguard_user_config_qr(ctx, username: str):
        logger.debug(f"Executing wireguard_user_config_qr command for user: {username}")
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