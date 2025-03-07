import psutil
import requests
import nextcord
from nextcord.ext import commands
import socket
from dotenv import load_dotenv
import os
from utils.decorators.auth import admin_or_higher
from utils.http_client import http_client
from infrastructure.logging import logger

# Load environment variables from .env file
load_dotenv()

# Get DOMAIN from environment variable
DOMAIN = os.getenv('DOMAIN')

# Check if DOMAIN is loaded correctly
if not DOMAIN:
    print("Warning: DOMAIN not found in environment variables. Please check your .env file.")

class SystemMonitoring(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="system_full_status", description="Zeigt detaillierte Systeminformationen an")
    @admin_or_higher()
    async def system_full_status(self, interaction: nextcord.Interaction):
        """Zeigt detaillierte Systeminformationen an"""
        logger.info(f"System full_status Befehl aufgerufen von {interaction.user.name}")
        
        try:
            # CPU, Memory, Disk usage
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Fetch Public IPv4 address
            try:
                public_ip = http_client.get("https://api.ipify.org?format=json").json()['ip']
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

            # Erstelle ein Embed für bessere Darstellung
            embed = nextcord.Embed(
                title="🖥️ System Status",
                description="Detaillierte Systeminformationen",
                color=0x00ff00 if cpu_percent < 70 else 0xff0000
            )
            
            embed.add_field(name="CPU", value=f"{cpu_percent}%", inline=True)
            embed.add_field(name="Memory", value=f"{memory.percent}%", inline=True)
            embed.add_field(name="Disk", value=f"{disk.percent}%", inline=True)
            embed.add_field(name="Public IPv4", value=public_ip, inline=False)
            embed.add_field(name="Domain", value=f"{DOMAIN} ({domain_ip})", inline=False)
            embed.add_field(name="IP Match", value=ip_match, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"System-Status abgerufen von {interaction.user.name}")
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Systemstatus: {e}")
            await interaction.response.send_message(f"Fehler beim Abrufen des Systemstatus: {str(e)}", ephemeral=True)

    @nextcord.slash_command(name="system_status", description="Zeigt grundlegende Systeminformationen an")
    @admin_or_higher()
    async def system_status(self, interaction: nextcord.Interaction):
        """Zeigt den Systemstatus an (CPU, Speicher, Festplatte)."""
        logger.info(f"System status Befehl aufgerufen von {interaction.user.name}")
        
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Erstelle ein Embed für bessere Darstellung
            embed = nextcord.Embed(
                title="🖥️ System Status",
                color=0x00ff00 if cpu_percent < 70 else 0xff0000
            )
            
            embed.add_field(name="CPU", value=f"{cpu_percent}%", inline=True)
            embed.add_field(name="Memory", value=f"{memory.percent}%", inline=True)
            embed.add_field(name="Disk", value=f"{disk.percent}%", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Basis-System-Status abgerufen von {interaction.user.name}")
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Systemstatus: {e}")
            await interaction.response.send_message(f"Fehler beim Abrufen des Systemstatus: {str(e)}", ephemeral=True)

    @nextcord.slash_command(name="system_ip", description="Zeigt die öffentliche IP-Adresse an")
    @admin_or_higher()
    async def system_public_ip(self, interaction: nextcord.Interaction):
        """Zeigt die öffentliche IP-Adresse an."""
        logger.info(f"System IP Befehl aufgerufen von {interaction.user.name}")
        
        try:
            public_ip = http_client.get("https://api.ipify.org?format=json").json()['ip']
            await interaction.response.send_message(f'Public IPv4: {public_ip}', ephemeral=True)
            logger.info(f"Öffentliche IP abgerufen von {interaction.user.name}")
        except requests.RequestException:
            await interaction.response.send_message("Unable to fetch public IP.", ephemeral=True)
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der öffentlichen IP: {e}")
            await interaction.response.send_message(f"Fehler beim Abrufen der öffentlichen IP: {str(e)}", ephemeral=True)

async def setup(bot):
    """Setup function for the system monitoring module"""
    try:
        cog = SystemMonitoring(bot)
        bot.add_cog(cog)  # Dies ist synchron, braucht kein await
        logger.info("System monitoring commands initialized successfully")
        return cog
    except Exception as e:
        logger.error(f"Failed to initialize system monitoring: {e}")
        raise