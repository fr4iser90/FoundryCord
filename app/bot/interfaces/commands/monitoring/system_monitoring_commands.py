import nextcord
from nextcord.ext import commands
from app.bot.interfaces.commands.decorators.auth import admin_or_higher
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

class SystemMonitoringCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.monitoring_service = bot.system_monitoring_service
    
    @nextcord.slash_command(name="system_full_status", description="Zeigt detaillierte Systeminformationen an")
    @admin_or_higher()
    async def system_full_status(self, interaction: nextcord.Interaction):
        """Zeigt detaillierte Systeminformationen an"""
        logger.info(f"System full_status Befehl aufgerufen von {interaction.user.name}")
        
        try:
            data = await self.monitoring_service.get_full_system_status()
            
            # Erstelle ein Embed für bessere Darstellung
            embed = nextcord.Embed(
                title="🖥️ System Status",
                description="Detaillierte Systeminformationen",
                color=0x00ff00 if data["cpu_percent"] < 70 else 0xff0000
            )
            
            embed.add_field(name="CPU", value=f"{data['cpu_percent']}%", inline=True)
            embed.add_field(name="Memory", value=f"{data['memory'].percent}%", inline=True)
            embed.add_field(name="Disk", value=f"{data['disk'].percent}%", inline=True)
            embed.add_field(name="Public IPv4", value=data["public_ip"], inline=False)
            embed.add_field(name="Domain", value=f"{data['domain']} ({data['domain_ip']})", inline=False)
            embed.add_field(name="IP Match", value=data["ip_match"], inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"System-Status abgerufen von {interaction.user.name}")
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen des Systemstatus: {e}")
            await interaction.response.send_message(f"Fehler beim Abrufen des Systemstatus: {str(e)}", ephemeral=True)

    @nextcord.slash_command(name="system_status", description="Zeigt grundlegende Systeminformationen an")
    @admin_or_higher()
    async def system_status(self, interaction: nextcord.Interaction):
        """Zeigt den Systemstatus an (CPU, Speicher, Festplatte)."""
        logger.info(f"System status Befehl aufgerufen von {interaction.user.name}")
        
        try:
            data = await self.monitoring_service.get_basic_system_status()
            
            # Erstelle ein Embed für bessere Darstellung
            embed = nextcord.Embed(
                title="🖥️ System Status",
                color=0x00ff00 if data["cpu_percent"] < 70 else 0xff0000
            )
            
            embed.add_field(name="CPU", value=f"{data['cpu_percent']}%", inline=True)
            embed.add_field(name="Memory", value=f"{data['memory'].percent}%", inline=True)
            embed.add_field(name="Disk", value=f"{data['disk'].percent}%", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Basis-System-Status abgerufen von {interaction.user.name}")
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen des Systemstatus: {e}")
            await interaction.response.send_message(f"Fehler beim Abrufen des Systemstatus: {str(e)}", ephemeral=True)

    @nextcord.slash_command(name="system_ip", description="Zeigt die öffentliche IP-Adresse an")
    @admin_or_higher()
    async def system_public_ip(self, interaction: nextcord.Interaction):
        """Zeigt die öffentliche IP-Adresse an."""
        logger.info(f"System IP Befehl aufgerufen von {interaction.user.name}")
        
        try:
            public_ip = await self.monitoring_service.get_public_ip()
            await interaction.response.send_message(f'Public IPv4: {public_ip}', ephemeral=True)
            logger.info(f"Öffentliche IP abgerufen von {interaction.user.name}")
        except requests.RequestException:
            await interaction.response.send_message("Unable to fetch public IP.", ephemeral=True)
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen der öffentlichen IP: {e}")
            await interaction.response.send_message(f"Fehler beim Abrufen der öffentlichen IP: {str(e)}", ephemeral=True)

async def setup(bot):
    """Setup function for the system monitoring commands"""
    try:
        # Check if system monitoring service exists and initialize if needed
        if not hasattr(bot, 'system_monitoring_service'):
            from app.bot.application.services.monitoring.system_monitoring import setup as setup_service
            bot.system_monitoring_service = await setup_service(bot)
            
        # Initialize commands (remove await from add_cog since it's not an async method)
        commands = SystemMonitoringCommands(bot)
        bot.add_cog(commands)  # Remove await - this is not an async method
        logger.info("System monitoring commands initialized successfully")
        return commands
    except Exception as e:
        logger.error(f"Failed to initialize system monitoring commands: {e}")
        raise