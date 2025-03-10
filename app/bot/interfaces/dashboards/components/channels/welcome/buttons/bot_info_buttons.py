import nextcord
from typing import Dict, Any
from interfaces.dashboards.components.common.buttons.base_button import BaseButton

class BotInfoButtons:
    """Button components for bot info view"""
    
    @staticmethod
    def create_system_button() -> BaseButton:
        """Create system features button"""
        return BaseButton(
            label="System Features",
            style=nextcord.ButtonStyle.primary,
            emoji="🖥️",
            custom_id="system_features",
            row=0
        )
    
    @staticmethod
    def create_dashboard_button() -> BaseButton:
        """Create dashboard features button"""
        return BaseButton(
            label="Dashboards",
            style=nextcord.ButtonStyle.primary,
            emoji="📊",
            custom_id="dashboard_features",
            row=0
        )
    
    # Add other buttons...
    
    @staticmethod
    def create_close_button() -> BaseButton:
        """Create close button"""
        return BaseButton(
            label="Close",
            style=nextcord.ButtonStyle.danger,
            emoji="✖️",
            custom_id="close_bot_info",
            row=2
        )
