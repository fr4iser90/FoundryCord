"""Dashboard embed component for displaying dashboard content."""

import discord
from typing import Optional, Dict, Any, ClassVar, List, Union

from app.shared.interface.logging.api import get_bot_logger
from app.bot.interfaces.dashboards.components.base_component import BaseComponent

logger = get_bot_logger()

class DashboardEmbed(BaseComponent):
    """Main dashboard embed for displaying dashboard content."""
    
    # Class variables
    COMPONENT_TYPE: ClassVar[str] = "dashboard_embed"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the dashboard embed.
        
        Args:
            config: Configuration for the dashboard embed
                - title: The title of the embed
                - description: The description of the embed
                - color: The color of the embed (in integer form)
                - fields: List of fields to add to the embed
                - image_url: Optional URL for the embed image
                - thumbnail_url: Optional URL for the embed thumbnail
                - footer: Optional footer text
                - author: Optional author configuration
        """
        default_config = {
            "title": "Dashboard",
            "description": "Dashboard information",
            "color": discord.Color.blurple().value,
            "fields": [],
            "image_url": None,
            "thumbnail_url": None,
            "footer": None,
            "author": None,
            "visible": True,
            "enabled": True,
        }
        
        super().__init__(config=config, default_config=default_config)
    
    def build(self) -> discord.Embed:
        """Build and return the Discord embed object.
        
        Returns:
            The built Discord embed
        """
        try:
            # Create the base embed
            embed = discord.Embed(
                title=self.config.get("title", "Dashboard"),
                description=self.config.get("description", ""),
                color=self.config.get("color", discord.Color.blurple().value)
            )
            
            # Add fields if provided
            fields = self.config.get("fields", [])
            for field in fields:
                embed.add_field(
                    name=field.get("name", "\u200b"),
                    value=field.get("value", "\u200b"),
                    inline=field.get("inline", True)
                )
            
            # Add image if provided
            if self.config.get("image_url"):
                embed.set_image(url=self.config["image_url"])
            
            # Add thumbnail if provided
            if self.config.get("thumbnail_url"):
                embed.set_thumbnail(url=self.config["thumbnail_url"])
            
            # Add footer if provided
            if self.config.get("footer"):
                if isinstance(self.config["footer"], dict):
                    embed.set_footer(
                        text=self.config["footer"].get("text", ""),
                        icon_url=self.config["footer"].get("icon_url")
                    )
                else:
                    embed.set_footer(text=str(self.config["footer"]))
                
            # Add author if provided
            if self.config.get("author"):
                if isinstance(self.config["author"], dict):
                    embed.set_author(
                        name=self.config["author"].get("name", ""),
                        url=self.config["author"].get("url"),
                        icon_url=self.config["author"].get("icon_url")
                    )
                else:
                    embed.set_author(name=str(self.config["author"]))
            
            # Add timestamp
            if self.config.get("timestamp", True):
                embed.timestamp = discord.utils.utcnow()
                
            return embed
            
        except Exception as e:
            logger.error(f"Error building dashboard embed: {str(e)}")
            # Return a minimal embed if we had an error building the proper one
            return discord.Embed(
                title="Dashboard Error",
                description="An error occurred while building this dashboard embed.",
                color=discord.Color.dark_gray()
            )
    
    def add_field(self, name: str, value: str, inline: bool = True) -> None:
        """Add a field to the embed configuration.
        
        Args:
            name: The name of the field
            value: The value of the field
            inline: Whether the field should be inline
        """
        if "fields" not in self.config:
            self.config["fields"] = []
            
        self.config["fields"].append({
            "name": name,
            "value": value,
            "inline": inline
        })
    
    def clear_fields(self) -> None:
        """Clear all fields from the embed configuration."""
        self.config["fields"] = []
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'DashboardEmbed':
        """Create a DashboardEmbed from serialized data.
        
        Args:
            data: The serialized data
            
        Returns:
            The created DashboardEmbed instance
        """
        return cls(config=data.get("config", {})) 