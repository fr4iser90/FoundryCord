"""Command for creating and managing dashboards."""
import nextcord
from nextcord.ext import commands
from nextcord import SlashOption

from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

class DashboardCommands(commands.Cog):
    """Commands for creating and managing dashboards."""
    
    def __init__(self, bot):
        self.bot = bot
        
    @nextcord.slash_command(
        name="dashboard",
        description="Dashboard management commands"
    )
    async def dashboard(self, interaction: nextcord.Interaction):
        """Dashboard management commands."""
        pass  # This is just the parent command
    
    @dashboard.subcommand(
        name="create",
        description="Create a dashboard in the current channel"
    )
    async def create_dashboard(
        self,
        interaction: nextcord.Interaction,
        dashboard_type: str = SlashOption(
            name="type",
            description="Dashboard type to create",
            required=True,
            choices={"System Monitoring": "monitoring",
                    "Welcome": "welcome",
                    "Project Management": "project",
                    "Game Hub": "gamehub"}
        )
    ):
        """Create a dashboard in the current channel."""
        await interaction.response.defer()
        
        try:
            # Check if dashboard registry exists
            if not hasattr(self.bot, "dashboard_registry"):
                # Create registry if needed
                from app.bot.infrastructure.dashboards.dashboard_registry import DashboardRegistry
                self.bot.dashboard_registry = DashboardRegistry(self.bot)
                await self.bot.dashboard_registry.initialize()
            
            # Create dashboard in current channel
            channel_id = interaction.channel.id
            result = await self.bot.dashboard_registry.activate_dashboard(
                dashboard_type=dashboard_type,
                channel_id=channel_id
            )
            
            if result:
                await interaction.followup.send(f"✅ {dashboard_type.capitalize()} dashboard created successfully!")
            else:
                await interaction.followup.send("❌ Failed to create dashboard. Check logs for details.")
                
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)}")
    
    @dashboard.subcommand(
        name="delete",
        description="Delete the dashboard in the current channel"
    )
    async def delete_dashboard(self, interaction: nextcord.Interaction):
        """Delete the dashboard in the current channel."""
        await interaction.response.defer()
        
        try:
            # Check if dashboard registry exists
            if not hasattr(self.bot, "dashboard_registry"):
                await interaction.followup.send("❌ No dashboards are active.")
                return
            
            # Delete dashboard in current channel
            channel_id = interaction.channel.id
            result = await self.bot.dashboard_registry.deactivate_dashboard(channel_id=channel_id)
            
            if result:
                await interaction.followup.send("✅ Dashboard removed successfully!")
            else:
                await interaction.followup.send("❌ No dashboard found in this channel.")
                
        except Exception as e:
            logger.error(f"Error deleting dashboard: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)}")

def setup(bot):
    """Add the cog to the bot."""
    bot.add_cog(DashboardCommands(bot)) 