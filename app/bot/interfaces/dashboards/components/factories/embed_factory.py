from typing import Dict, Any, Optional
import nextcord
from datetime import datetime

from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

from app.bot.interfaces.dashboards.components.common.embeds.dashboard_embed import DashboardEmbed

from app.bot.infrastructure.factories.base.base_factory import BaseFactory

class EmbedFactory(BaseFactory):
    """Factory for creating embed UI components."""
    
    def __init__(self, bot):
        self.bot = bot
    
    def create(self, title: str = None, description: str = None, color: str = None, 
              fields: list = None, footer: Dict[str, Any] = None, **kwargs):
        """Create an embed component."""
        try:
            # Convert color string to int if provided
            color_int = None
            if color:
                if color.startswith('0x'):
                    color_int = int(color, 16)
                else:
                    color_int = int(color)
            
            # Create embed
            embed = nextcord.Embed(
                title=title,
                description=description,
                color=color_int or 0x3498db,
                **kwargs
            )
            
            # Add fields if provided
            if fields:
                for field in fields:
                    embed.add_field(
                        name=field.get('name', ''),
                        value=field.get('value', ''),
                        inline=field.get('inline', False)
                    )
            
            # Add footer if provided
            if footer:
                embed.set_footer(
                    text=footer.get('text'),
                    icon_url=footer.get('icon_url')
                )
                
            # Add timestamp if not specified
            if 'timestamp' not in kwargs:
                embed.timestamp = datetime.now()
            
            return embed
            
        except Exception as e:
            logger.error(f"Error creating embed: {e}")
            return nextcord.Embed(title="Error", description=f"Failed to create embed: {e}", color=0xff0000)
