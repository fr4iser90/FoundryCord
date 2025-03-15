from typing import Optional
import nextcord
from datetime import datetime
from .base_embed import BaseEmbed

class DashboardEmbed(BaseEmbed):
    """Standard embed for dashboard UI components"""
    
    @classmethod
    def add_standard_footer(cls, embed: nextcord.Embed, text: str = "HomeLab Discord • Last Updated"):
        """Adds the standard footer with timestamp to an embed"""
        embed.set_footer(text=text)
        embed.timestamp = nextcord.utils.utcnow()
        return embed
    
    @classmethod
    def create_dashboard_embed(cls, title: str, description: Optional[str] = None, color: Optional[int] = None, add_footer: bool = True) -> nextcord.Embed:
        """Creates a standard dashboard embed with optional footer"""
        embed = cls.create(
            title=title,
            description=description,
            color=color or cls.INFO_COLOR,
        )
        
        if add_footer:
            cls.add_standard_footer(embed)
            
        return embed
