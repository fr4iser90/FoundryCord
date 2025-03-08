import nextcord
from typing import Optional, Callable, List
from infrastructure.logging import logger
from .base_view import BaseView

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
            style=nextcord.ButtonStyle.primary,
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
        
        # Role select menu
        role_select = nextcord.ui.RoleSelect(
            placeholder="Select your roles",
            custom_id="welcome_roles",
            min_values=0,
            max_values=10,
            row=1
        )
        role_select.callback = lambda i: self._handle_callback(i, "role_select")
        self.add_item(role_select)
        
        return self
