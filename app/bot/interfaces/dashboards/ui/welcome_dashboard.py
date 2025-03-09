from typing import Optional, List
import nextcord
from .base_dashboard import BaseDashboardUI
from interfaces.dashboards.components.channels.welcome.views import WelcomeView
from infrastructure.logging import logger

class WelcomeDashboardUI(BaseDashboardUI):
    """UI class for displaying the homelab welcome dashboard"""
    
    DASHBOARD_TYPE = "welcome"
    TITLE_IDENTIFIER = "Homelab Welcome"
    
    def __init__(self, bot):
        super().__init__(bot)
        self.service = None
        self.initialized = False
    
    def set_service(self, service):
        """Sets the service for this UI component"""
        self.service = service
        return self
    
    async def initialize(self) -> None:
        """Initializes the UI component"""
        self.initialized = True
        logger.info("Welcome Dashboard UI initialized")
        return await super().initialize(channel_config_key='welcome')
    
    async def create_embed(self) -> nextcord.Embed:
        """Creates the enhanced homelab welcome dashboard embed"""
        # Get guild info
        guild = self.channel.guild if self.channel else None
        member_count = guild.member_count if guild else 0
        
        # Create the main embed with homelab branding
        embed = nextcord.Embed(
            title=f"🏠 {self.TITLE_IDENTIFIER} - {guild.name if guild else 'Homelab'} Server",
            description=(
                f"👋 **Welcome to our Homelab Community!**\n\n"
                f"This is a place for homelab enthusiasts, self-hosting fans, and tech tinkerers."
            ),
            color=0x3498db  # A nice blue color
        )
        
        # Add server stats section
        embed.add_field(
            name="📊 Server Stats",
            value=(
                f"👥 **Members:** {member_count}\n"
                f"🔧 **Bot Prefix:** `!`\n"
                f"📅 **Established:** {guild.created_at.strftime('%d.%m.%Y') if guild else 'Unknown'}"
            ),
            inline=False
        )
        
        # Add homelab resources section
        embed.add_field(
            name="🖥️ Homelab Resources",
            value=(
                "• Use `/homelab monitoring status` to check system status\n"
                "• Check out <#projects> for ongoing projects\n"
                "• Join <#infrastructure> for documentation\n"
                "• Ask for help in <#support>"
            ),
            inline=False
        )
        
        # Add registration instructions
        embed.add_field(
            name="🔐 Getting Started",
            value=(
                "1. Click the **Accept Rules** button below\n"
                "2. Select your tech interests from the dropdown\n"
                "3. Check out `/help` for available commands\n"
                "4. Introduce yourself in <#introductions>"
            ),
            inline=False
        )
        
        # Server links/resources
        embed.add_field(
            name="🔗 Useful Links",
            value=(
                "[Homelab Wiki](https://homelab.wiki)\n"
                "[Self-Hosted Resources](https://reddit.com/r/selfhosted)\n"
                "[Server Documentation](https://docs.example.com)"
            ),
            inline=False
        )
        
        # Set footer with timestamp
        embed.set_footer(text="HomeLab Discord • Last Updated")
        embed.timestamp = nextcord.utils.utcnow()
        
        return embed
    
    def create_view(self) -> nextcord.ui.View:
        """Create a view with welcome components"""
        # Create welcome view
        welcome_view = WelcomeView(guild_name=self.channel.guild.name if self.channel else "Homelab Server")
        view = welcome_view.create()
        
        # Register callbacks - make sure to use await
        # THIS IS WRONG: self.register_callbacks(view)
        # Instead, do this in your display_dashboard method
        
        return view
    
    async def on_rules_accept(self, interaction: nextcord.Interaction):
        """Handler for rule acceptance button"""
        # Add 'Member' role when accepting rules
        try:
            member_role = nextcord.utils.get(interaction.guild.roles, name="Member")
            if member_role:
                await interaction.user.add_roles(member_role)
                await interaction.response.send_message(
                    "✅ Thanks for accepting the rules! You now have access to the server.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "✅ Rules accepted! (Note: Member role not found)",
                    ephemeral=True
                )
                
            # Log the acceptance
            log_channel = nextcord.utils.get(interaction.guild.channels, name="bot-logs")
            if log_channel:
                await log_channel.send(f"📝 {interaction.user.mention} accepted the rules")
                
        except Exception as e:
            logger.error(f"Error in rule acceptance: {e}")
            await interaction.response.send_message("Error processing your request.", ephemeral=True)
    
    async def on_role_select(self, interaction: nextcord.Interaction):
        """Handler for tech role selection"""
        # Get selected roles from dropdown
        try:
            selected_roles = interaction.data.get("values", [])
            
            # Role mapping (role_id to actual Discord role names)
            role_mapping = {
                "server_admin": "Server Admin",
                "network_eng": "Network Engineer",
                "docker": "Docker User",
                "game_servers": "Game Server Host",
                "linux": "Linux Enthusiast",
                "windows": "Windows User",
                "virtualization": "Virtualization",
                "home_automation": "Home Automation",
                "security": "Security Specialist",
                "iot": "IoT Enthusiast"
            }
            
            # Add roles to user
            roles_added = []
            roles_failed = []
            
            for role_id in selected_roles:
                if role_id in role_mapping:
                    role_name = role_mapping[role_id]
                    role = nextcord.utils.get(interaction.guild.roles, name=role_name)
                    
                    if role:
                        await interaction.user.add_roles(role)
                        roles_added.append(role_name)
                    else:
                        roles_failed.append(role_name)
            
            # Prepare response
            if roles_added:
                response = f"✅ Added roles: {', '.join(roles_added)}"
                if roles_failed:
                    response += f"\n⚠️ Could not add (roles not found): {', '.join(roles_failed)}"
            else:
                response = "⚠️ Could not add any roles. Please contact an admin."
                
            await interaction.response.send_message(response, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in role selection: {e}")
            await interaction.response.send_message("Error processing your request.", ephemeral=True)
    
    async def on_server_info(self, interaction: nextcord.Interaction):
        """Handler for server info button"""
        guild = interaction.guild
        
        # Get server stats
        member_count = guild.member_count
        online_count = sum(1 for m in guild.members if m.status != nextcord.Status.offline)
        channel_count = len(guild.channels)
        
        # Create detailed server info
        info_embed = nextcord.Embed(
            title=f"📊 {guild.name} Server Information",
            description=f"Detailed information about our homelab community server.",
            color=0x3498db
        )
        
        info_embed.add_field(
            name="📈 Statistics",
            value=(
                f"👥 **Members:** {member_count}\n"
                f"🟢 **Online:** {online_count}\n"
                f"💬 **Channels:** {channel_count}\n"
                f"📅 **Created:** {guild.created_at.strftime('%d.%m.%Y')}"
            ),
            inline=False
        )
        
        info_embed.add_field(
            name="🏆 Server Features",
            value=(
                "• System monitoring dashboard\n"
                "• Project management\n"
                "• Game server status tracking\n"
                "• Infrastructure documentation\n"
                "• Automated alerts"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=info_embed, ephemeral=True)
    
    async def on_help_request(self, interaction: nextcord.Interaction):
        """Handler for help button"""
        help_text = (
            "## Available Commands\n"
            "• `/homelab monitoring status` - View system status\n"
            "• `/homelab projects list` - Manage projects\n" 
            "• `/homelab servers status` - Server management\n\n"
            "## Support\n"
            "If you need assistance, ask in <#support> or tag the @Admin role."
        )
        
        await interaction.response.send_message(help_text, ephemeral=True)
    
    async def register_callbacks(self, view):
        """Register callbacks for the view components"""
        view.set_callback("accept_rules", self.on_rules_accept)
        view.set_callback("welcome_help", self.on_help_request)
        view.set_callback("server_info", self.on_server_info)
        #view.set_callback("tech_select", self.on_tech_select)
    
    async def display_dashboard(self) -> None:
        """Displays the welcome dashboard in the configured channel"""
        try:
            if not self.channel:
                logger.error("No channel configured for welcome dashboard")
                return
            
            # Clean up old dashboards first
            await self.cleanup_old_dashboards(keep_count=1)
            
            # Create embed and view
            embed = await self.create_embed()
            view = self.create_view()
            
            # Register callbacks - with await
            await self.register_callbacks(view)
            
            # If we have an existing message, update it
            if self.message and hasattr(self.message, 'edit'):
                try:
                    await self.message.edit(embed=embed, view=view)
                    logger.info(f"Updated existing welcome dashboard in {self.channel.name}")
                    return
                except Exception as e:
                    logger.warning(f"Couldn't update existing message: {e}, creating new")
            
            # Otherwise send a new message
            try:
                message = await self.channel.send(embed=embed, view=view)
                self.message = message
                
                # Track in dashboard manager
                await self.bot.dashboard_manager.track_message(
                    dashboard_type=self.DASHBOARD_TYPE,
                    message_id=message.id,
                    channel_id=self.channel.id
                )
                
                logger.info(f"Welcome dashboard displayed in channel {self.channel.name}")
            except Exception as e:
                logger.error(f"Error sending welcome dashboard: {e}")
            
        except Exception as e:
            logger.error(f"Error displaying welcome dashboard: {e}")
