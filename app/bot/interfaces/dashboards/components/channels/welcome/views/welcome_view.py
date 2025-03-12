import nextcord
from typing import Optional, Callable, List
from app.bot.infrastructure.logging import logger
from app.bot.interfaces.dashboards.components.common.views import BaseView


class WelcomeView(BaseView):
    """View for welcome dashboard with role selection and info buttons"""
    
    def __init__(
        self,
        guild_name: str = None,
        timeout: Optional[int] = None
    ):
        super().__init__(timeout=timeout)
        self.guild_name = guild_name
    
    def create(self):
        """Create the view with all welcome components"""
        # Rules accept button
        rules_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.success,
            label="Accept Rules",
            emoji="✅",
            custom_id="accept_rules",
            row=0
        )
        rules_button.callback = lambda i: self._handle_callback(i, "accept_rules")
        self.add_item(rules_button)
        
        # Help button
        help_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.secondary,
            label="Help",
            emoji="❓",
            custom_id="welcome_help",
            row=0
        )
        help_button.callback = lambda i: self._handle_callback(i, "help")
        self.add_item(help_button)
        
        # Server info button
        info_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Server Info",
            emoji="ℹ️",
            custom_id="server_info",
            row=0
        )
        info_button.callback = lambda i: self._handle_callback(i, "server_info")
        self.add_item(info_button)
        
        # Bot info button
        bot_info_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.primary,
            label="Bot Info",
            emoji="🤖",
            custom_id="bot_info",
            row=0
        )
        bot_info_button.callback = lambda i: self._handle_callback(i, "bot_info")
        self.add_item(bot_info_button)
        
        # homelab-tech-specific roles select
        tech_select = nextcord.ui.StringSelect(
            placeholder="Select your tech interests...",
            custom_id="tech_interests",
            min_values=0,
            max_values=5,
            options=[
                nextcord.SelectOption(
                    label="Linux User",
                    value="linux_user",
                    emoji="🐧",
                    description="Experienced with Linux systems"
                ),
                nextcord.SelectOption(
                    label="Docker",
                    value="docker_user",
                    emoji="🐳",
                    description="Docker container enthusiast"
                ),
                nextcord.SelectOption(
                    label="Network Admin",
                    value="network_admin",
                    emoji="🌐",
                    description="Network administration skills"
                ),
                nextcord.SelectOption(
                    label="Game Server Host",
                    value="game_server",
                    emoji="🎮",
                    description="Hosts game servers"
                ),
                nextcord.SelectOption(
                    label="Home Automation",
                    value="home_automation",
                    emoji="🏠",
                    description="Smart home enthusiast"
                )
            ],
            row=1
        )
        tech_select.callback = lambda i: self._handle_callback(i, "tech_select")
        self.add_item(tech_select)
        
        # Role select menu
        # role_select = nextcord.ui.RoleSelect(
        #     placeholder="Select additional server roles",
        #     custom_id="welcome_roles",
        #     min_values=0,
        #     max_values=5,
        #     row=2
        # )
        # role_select.callback = lambda i: self._handle_callback(i, "role_select")
        # self.add_item(role_select)
        
        return self
