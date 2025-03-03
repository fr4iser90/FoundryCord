import psutil
import requests
from nextcord.ext import commands
import socket
from dotenv import load_dotenv
import os
from core.decorators.auth import admin_only
from core.decorators.respond import respond_in_channel, respond_using_config, respond_in_dm, respond_encrypted_in_dm, respond_with_file 

# Load environment variables from .env file
load_dotenv()

# Get DOMAIN from environment variable
DOMAIN = os.getenv('DOMAIN')

# Check if DOMAIN is loaded correctly
if not DOMAIN:
    print("Warning: DOMAIN not found in environment variables. Please check your .env file.")

def setup(bot):
    # Add status command to bot
    @bot.command(name='system_full_status')
    @admin_only()  # Nur Admins dürfen diesen Befehl ausführen
    async def status(ctx):
        # CPU, Memory, Disk usage
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Fetch Public IPv4 address
        try:
            public_ip = requests.get("https://api.ipify.org?format=json").json()['ip']
        except requests.RequestException:
            public_ip = "Unable to fetch public IP"

        # Check if the public IP matches the domain (simplified check)
        try:
            if DOMAIN:
                # Get the IP of the domain
                domain_ip = socket.gethostbyname(DOMAIN)
                ip_match = "matches" if public_ip == domain_ip else "does not match"
            else:
                domain_ip = "No DOMAIN configured"
                ip_match = "N/A"
        except socket.gaierror:
            domain_ip = "Unable to resolve domain"
            ip_match = "N/A"

        # Send the status to the Discord channel
        await ctx.send(f'CPU Usage: {cpu_percent}%\n'
                       f'Memory Usage: {memory.percent}%\n'
                       f'Disk Usage: {disk.percent}%\n'
                       f'Public IPv4: {public_ip}\n'
                       f'DOMAIN: {DOMAIN}\n'
                       f'{DOMAIN} IP: {domain_ip} ({ip_match})')

    @bot.command(name='system_status')
    @admin_only()
    @respond_in_dm()
    async def system_status(ctx):
        """Zeigt den Systemstatus an (CPU, Speicher, Festplatte)."""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return (
            f'CPU Usage: {cpu_percent}%\n'
            f'Memory Usage: {memory.percent}%\n'
            f'Disk Usage: {disk.percent}%'
        )

    @bot.command(name='system_public_ip')
    @admin_only()
    async def system_public_ip(ctx):
        """Zeigt die öffentliche IP-Adresse an."""
        try:
            public_ip = requests.get("https://api.ipify.org?format=json").json()['ip']
            await ctx.send(f'Public IPv4: {public_ip}')
        except requests.RequestException:
            await ctx.send("Unable to fetch public IP.")