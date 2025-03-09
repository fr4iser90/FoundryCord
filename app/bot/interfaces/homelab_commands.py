import nextcord
from nextcord.ext import commands
from utils.decorators.auth import admin_or_higher
from infrastructure.logging import logger

class HomelabCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Main command group
    @nextcord.slash_command(name="homelab", description="Homelab management commands")
    async def homelab(self, interaction: nextcord.Interaction):
        """Base command for homelab management"""
        pass  # This serves as the base command and won't be executed directly
    
    # Server command group
    @nextcord.slash_command(name="homelab_servers_status", description="Check status of all servers")
    @admin_or_higher()
    async def server_status(self, interaction: nextcord.Interaction):
        """Display status information for all servers"""
        await interaction.response.send_message("Fetching server status...", ephemeral=True)
        # Implementation will be added later
    
    @nextcord.slash_command(name="homelab_servers_restart", description="Restart a specific server")
    @admin_or_higher()
    async def server_restart(
        self, 
        interaction: nextcord.Interaction, 
        server_name: str = nextcord.SlashOption(description="Name of the server to restart")
    ):
        """Restart a specific server"""
        await interaction.response.send_message(f"Restarting server {server_name}...", ephemeral=True)
        # Implementation will be added later
    
    # Container command group
    @nextcord.slash_command(name="homelab_containers_list", description="List all Docker containers")
    @admin_or_higher()
    async def container_list(self, interaction: nextcord.Interaction):
        """List all Docker containers and their status"""
        await interaction.response.send_message("Fetching container list...", ephemeral=True)
        # Implementation will be added later
    
    @nextcord.slash_command(name="homelab_containers_restart", description="Restart a Docker container")
    @admin_or_higher()
    async def container_restart(
        self,
        interaction: nextcord.Interaction,
        container_name: str = nextcord.SlashOption(description="Name of the container to restart")
    ):
        """Restart a specific Docker container"""
        await interaction.response.send_message(f"Restarting container {container_name}...", ephemeral=True)
        # Implementation will be added later
    
    # Monitoring command group
    @nextcord.slash_command(name="homelab_monitoring_status", description="Show current system status")
    async def monitoring_status(self, interaction: nextcord.Interaction):
        """Display current system status (CPU, RAM, disk usage)"""
        await interaction.response.send_message("Fetching system status...", ephemeral=True)
        # Implementation will be added later
    
    # Help command
    @nextcord.slash_command(name="homelab_help", description="Display help information")
    async def help_command(self, interaction: nextcord.Interaction):
        """Display help information for homelab commands"""
        embed = nextcord.Embed(
            title="Homelab Commands Help",
            description="Here are all available homelab commands:",
            color=0x3498db
        )
        
        embed.add_field(
            name="🖥️ Server Management",
            value=(
                "`/homelab_servers_status` - Check all servers\n"
                "`/homelab_servers_restart` - Restart a server"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🐳 Container Management",
            value=(
                "`/homelab_containers_list` - List all containers\n"
                "`/homelab_containers_restart` - Restart a container"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📊 Monitoring",
            value=(
                "`/homelab_monitoring_status` - View system status"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    """Setup function for homelab commands"""
    try:
        commands = HomelabCommands(bot)
        bot.add_cog(commands)
        logger.info("Homelab commands registered successfully")
        return commands  # Return the commands instance, not just True
    except Exception as e:
        logger.error(f"Failed to register homelab commands: {e}")
        raise