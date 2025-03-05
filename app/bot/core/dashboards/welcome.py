from typing import Optional
import nextcord

class WelcomeDashboard:
    def __init__(self, bot):
        self.bot = bot
        self.dashboard_factory = bot.component_factory.factories['dashboard']

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
            
            # Notification preferences
            {
                'type': 'role_menu',
                'custom_id': 'notification_roles',
                'placeholder': '🔔 Select notification preferences',
                'min_values': 0,
                'max_values': 3
            },
            
            # Quick actions
            {
                'type': 'button',
                'label': 'Server Info',
                'custom_id': 'server_info',
                'emoji': 'ℹ️',
                'style': nextcord.ButtonStyle.blurple
            },
            {
                'type': 'button',
                'label': 'Help',
                'custom_id': 'help_menu',
                'emoji': '❓',
                'style': nextcord.ButtonStyle.gray
            }
        ]

        # Event handlers für die Komponenten
        async def on_rules_accept(interaction: nextcord.Interaction):
            await interaction.response.send_message("Rules accepted!", ephemeral=True)
            # Hier Logik für Regelakzeptanz

        async def on_role_select(interaction: nextcord.Interaction):
            roles = interaction.data["values"]
            await interaction.response.send_message(f"Selected roles: {', '.join(roles)}", ephemeral=True)
            # Hier Logik für Rollenzuweisung

        async def on_server_info(interaction: nextcord.Interaction):
            await interaction.response.send_message(
                f"Server Info for {interaction.guild.name}\n"
                f"Members: {interaction.guild.member_count}\n"
                f"Created: {interaction.guild.created_at.strftime('%d.%m.%Y')}", 
                ephemeral=True
            )

        # Dashboard erstellen und senden
        embed, view = await self.dashboard_factory.create_dashboard(
            title=f"Welcome to {channel.guild.name}",
            description=description,
            components=components,
            color=0x5865F2  # Discord Blurple
        )

        # Event handler registrieren
        view.children[0].callback = on_rules_accept  # Rules button
        view.children[1].callback = on_role_select   # Role menu
        view.children[2].callback = on_role_select   # Notification menu
        view.children[3].callback = on_server_info   # Server info button

        return await channel.send(embed=embed, view=view)