import nextcord
from nextcord.ext import commands
from application.services.monitoring_application_service import MonitoringApplicationService
from utils.decorators.auth import admin_or_higher

class SystemMonitoringCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.monitoring_service = bot.monitoring_service
    
    @nextcord.slash_command(name="system_full_status", description="Zeigt detaillierte Systeminformationen an")
    @admin_or_higher()
    async def system_full_status(self, interaction: nextcord.Interaction):
        """Zeigt detaillierte Systeminformationen an"""
        # Use monitoring application service to get data and create response
        data = await self.monitoring_service.get_full_system_status()
        
        # Create embed from data
        embed = self._create_full_status_embed(data)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Add other commands...
    
    def _create_full_status_embed(self, data):
        # Create embed with the data
        # Similar to your current implementation
        pass

async def setup(bot):
    await bot.add_cog(SystemMonitoringCommands(bot))