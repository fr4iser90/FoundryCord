from typing import Optional, Dict, Any
import nextcord
from datetime import datetime
from .base_embed import BaseEmbed
from app.bot.interfaces.dashboards.components.common.base_component import BaseComponent

class DashboardEmbed(BaseComponent):
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

    async def create(self, ctx: Optional[nextcord.Interaction] = None) -> nextcord.Embed:
        """Create a dashboard embed"""
        title = self.get_config_value('title', 'Dashboard')
        description = self.get_config_value('description', '')
        color = self.get_config_value('color', nextcord.Color.blurple())
        
        if isinstance(color, str) and color.startswith('#'):
            # Convert hex color to nextcord.Color
            color = nextcord.Color.from_str(color)
        elif isinstance(color, int):
            color = nextcord.Color(color)
        
        embed = nextcord.Embed(
            title=title,
            description=description,
            color=color
        )
        
        # Add fields if defined in config
        fields = self.get_config_value('fields', [])
        for field in fields:
            name = field.get('name', 'Field')
            value = field.get('value', 'No value')
            inline = field.get('inline', False)
            embed.add_field(name=name, value=value, inline=inline)
            
        # Add footer if defined
        footer_text = self.get_config_value('footer', None)
        if footer_text:
            embed.set_footer(text=footer_text)
            
        # Add timestamp if enabled
        if self.get_config_value('timestamp', False):
            embed.timestamp = nextcord.utils.utcnow()
            
        return embed
    
    async def update(self, data: Any, ctx: Optional[nextcord.Interaction] = None) -> nextcord.Embed:
        """Update the embed with new data"""
        # For embeds, we'll typically recreate it with updated config
        if isinstance(data, dict):
            # Update config with new data
            self.config.update(data)
        
        # Create a fresh embed with updated config
        return await self.create(ctx)
