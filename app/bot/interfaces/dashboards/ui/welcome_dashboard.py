from typing import Optional
import nextcord
from .base_dashboard import BaseDashboardUI
from interfaces.dashboards.components.views.welcome_view import WelcomeView

class WelcomeDashboardUI(BaseDashboardUI):
    """UI class for displaying the welcome dashboard"""
    
    DASHBOARD_TYPE = "welcome"
    TITLE_IDENTIFIER = "Welcome"
    
    async def initialize(self):
        """Initialize the welcome dashboard UI"""
        return await super().initialize(channel_config_key='welcome')
    
    async def create(self, channel, member_count: int):
        """Creates the welcome dashboard with all components"""
        
        description = (
            f"👋 **Welcome to {channel.guild.name}!**\n\n"
            f"🎮 Current Members: {member_count}\n"
            "📌 Bot Prefix: `!`\n\n"
            "Please select your roles and accept our rules below.\n"
            "Need help? Click the help button or use `/help`!"
        )

        components = [
            # Rules acceptance
            {
                'type': 'button',
                'label': 'Accept Rules',
                'custom_id': 'accept_rules',
                'emoji': '✅',
                'style': nextcord.ButtonStyle.green
            },
            
            # Main role selection
            {
                'type': 'role_menu',
                'custom_id': 'select_roles',
                'placeholder': '🎭 Select your roles',
                'min_values': 0,
                'max_values': 5
            },
            
            # Additional components...
        ]

        # Create and return the dashboard
        embed, view = await self.dashboard_factory.create_dashboard(
            title=f"Welcome to {channel.guild.name}",
            description=description,
            components=components,
            color=0x5865F2
        )

        # Register event handlers
        self._register_handlers(view)

        return await channel.send(embed=embed, view=view)
        
    def _register_handlers(self, view):
        """Register event handlers for dashboard components"""
        view.children[0].callback = self._on_rules_accept
        view.children[1].callback = self._on_role_select
        # Register other handlers...
        
    async def _on_rules_accept(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("Rules accepted!", ephemeral=True)
        # Logic for rule acceptance
        
    async def _on_role_select(self, interaction: nextcord.Interaction):
        roles = interaction.data["values"]
        await interaction.response.send_message(f"Selected roles: {', '.join(roles)}", ephemeral=True)
        # Logic for role assignment

    def create_view(self) -> nextcord.ui.View:
        view = WelcomeView(guild_name=self.channel.guild.name)
        self.register_callbacks(view)
        return view.create()
    
    async def on_rules_accept(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("Rules accepted!", ephemeral=True)
        # Logic for rule acceptance
    
    async def on_role_select(self, interaction: nextcord.Interaction):
        roles = interaction.data["values"]
        await interaction.response.send_message(f"Selected roles: {', '.join(roles)}", ephemeral=True)
        # Logic for role assignment
    
    async def on_server_info(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            f"Server Info for {interaction.guild.name}\n"
            f"Members: {interaction.guild.member_count}\n"
            f"Created: {interaction.guild.created_at.strftime('%d.%m.%Y')}", 
            ephemeral=True
        )
    
    async def register_callbacks(self, view):
        """Register callbacks for the view"""
        view.set_callback("accept_rules", self.on_rules_accept)
        view.set_callback("select_roles", self.on_role_select)
        view.set_callback("server_info", self.on_server_info)
        # Register other callbacks
