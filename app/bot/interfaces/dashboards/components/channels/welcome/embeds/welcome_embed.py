from typing import Optional
import nextcord
from datetime import datetime
from interfaces.dashboards.components.common.embeds import BaseEmbed

class WelcomeEmbed(BaseEmbed):
    """Welcome specific embed implementations"""
    
    @classmethod
    def create_welcome(cls, guild_name: str, member_count: int) -> nextcord.Embed:
        """Creates the welcome dashboard embed"""
        description = (
            f"👋 **Welcome to {guild_name}!**\n\n"
            f"🎮 Current Members: {member_count}\n"
            "📌 Bot Prefix: `!`\n\n"
            "Please select your roles and accept our rules below.\n"
            "Need help? Click the help button or use `/help`!"
        )
        
        return cls.create(
            title=f"Welcome to {guild_name}",
            description=description,
            color=0x5865F2,  # Discord Blurple
            footer="Thanks for joining us!"
        )