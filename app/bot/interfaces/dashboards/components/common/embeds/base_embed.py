from typing import Optional, Dict, Any
import nextcord
from datetime import datetime
from app.shared.logging import logger

class BaseEmbed:
    """Base class for all dashboard embeds"""
    
    DEFAULT_COLOR = 0x2ecc71
    ERROR_COLOR = 0xff0000
    WARNING_COLOR = 0xf1c40f
    SUCCESS_COLOR = 0x2ecc71
    INFO_COLOR = 0x3498db
    
    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        color: Optional[int] = None,
        fields: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        footer: Optional[str] = None
    ) -> nextcord.Embed:
        """Creates a base embed with common properties"""
        try:
            embed = nextcord.Embed(
                title=title,
                description=description,
                color=color or cls.DEFAULT_COLOR,
                timestamp=timestamp or datetime.now()
            )
            
            if fields:
                for name, field_data in fields.items():
                    embed.add_field(
                        name=name,
                        value=field_data.get('value', ''),
                        inline=field_data.get('inline', True)
                    )
                    
            if footer:
                embed.set_footer(text=footer)
                
            return embed
            
        except Exception as e:
            logger.error(f"Error creating embed: {e}")
            return cls.create_error()

    @classmethod
    def create_error(
        cls,
        title: str = "⚠️ Error",
        description: str = "An error occurred while processing your request."
    ) -> nextcord.Embed:
        return cls.create(title=title, description=description, color=cls.ERROR_COLOR)
