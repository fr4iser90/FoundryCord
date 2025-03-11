from typing import Optional
import nextcord
from datetime import datetime
from .base_embed import BaseEmbed

class DashboardEmbed(BaseEmbed):
    """Dashboard specific embed implementations with standardized footer"""
    
    @classmethod
    def add_standard_footer(cls, embed: nextcord.Embed, text: str = "HomeLab Discord • Last Updated"):
        """Adds the standard footer with timestamp to an embed"""
        embed.set_footer(text=text)
        embed.timestamp = nextcord.utils.utcnow()
        return embed
    
    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        color: Optional[int] = None,
        fields: Optional[dict] = None,
        add_footer: bool = True
    ) -> nextcord.Embed:
        """Creates a dashboard embed with standard footer"""
        embed = super().create(
            title=title,
            description=description,
            color=color or cls.INFO_COLOR,
            fields=fields
        )
        
        if add_footer:
            cls.add_standard_footer(embed)
            
        return embed
