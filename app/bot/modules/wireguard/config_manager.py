import psutil
import requests
from nextcord.ext import commands
import socket
from dotenv import load_dotenv
import os
import subprocess
from modules.utilities.logger import logger
from modules.auth.decorators import admin_only, respond_in_dm, respond_in_dm_in_codeblock

# Load environment variables from .env file
load_dotenv()

# Get DOMAIN from environment variable
DOMAIN = os.getenv('DOMAIN')

# Check if DOMAIN is loaded correctly
if not DOMAIN:
    logger.warning("DOMAIN not found in environment variables. Please check your .env file.")

def setup(bot):
    logger.info(f"Setting up wireguard_config command (Bot ID: {id(bot)})")
    @bot.command(name='wireguard_config')
    @admin_only()
    @respond_in_dm_in_codeblock()
    async def wireguard_config(ctx):
        logger.debug("Executing wireguard_config command")
        config_path = "/app/bot/database/wireguard/wg0.conf"
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_content = f.read()
            
            logger.debug(f"Returning config content (Length: {len(config_content)} chars)")
            return config_content.strip()
        else:
            logger.warning(f"Config file not found at path: {config_path}")
            return "Die WireGuard-Konfigurationsdatei konnte nicht gefunden werden."
