import nextcord
from typing import Dict, Any
from app.bot.interfaces.dashboards.components.common.buttons.base_button import BaseButton

class WelcomeButtons:
    """Button components for welcome dashboard"""
    
    @staticmethod
    def create_rules_button() -> BaseButton:
        """Create rules accept button"""
        return BaseButton(
            label="Accept Rules",
            style=nextcord.ButtonStyle.success,
            emoji="✅",
            custom_id="accept_rules",
            row=0
        )
    
    @staticmethod
    def create_help_button() -> BaseButton:
        """Create help button"""
        return BaseButton(
            label="Help",
            style=nextcord.ButtonStyle.secondary,
            emoji="❓",
            custom_id="welcome_help",
            row=0
        )
    
    @staticmethod
    def create_server_info_button() -> BaseButton:
        """Create server info button"""
        return BaseButton(
            label="Server Info",
            style=nextcord.ButtonStyle.primary,
            emoji="ℹ️",
            custom_id="server_info",
            row=0
        )
    
    @staticmethod
    def create_bot_info_button() -> BaseButton:
        """Create bot info button"""
        return BaseButton(
            label="Bot Info",
            style=nextcord.ButtonStyle.primary,
            emoji="🤖",
            custom_id="bot_info",
            row=0
        )
