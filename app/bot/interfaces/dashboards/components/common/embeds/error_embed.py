"""Error embed component for displaying error messages in dashboards."""

import discord
from typing import Optional, Dict, Any, ClassVar

from app.shared.interface.logging.api import get_bot_logger
from app.bot.interfaces.dashboards.components.base_component import BaseComponent

logger = get_bot_logger()

class ErrorEmbed(BaseComponent):
    """Error embed for displaying error messages."""
    
    # Class variables
    COMPONENT_TYPE: ClassVar[str] = "error_embed"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the error embed.
        
        Args:
            config: Configuration for the error embed
                - title: The title of the embed
                - description: The description/message of the embed
                - color: The color of the embed (in integer form)
                - error_code: Optional error code to display
                - footer: Optional footer text
        """
        default_config = {
            "title": "Error",
            "description": "An error occurred",
            "color": discord.Color.red().value,
            "error_code": None,
            "footer": None,
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
                title=self.config["title"],
                description=self.config["description"],
                color=self.config["color"]
            )
            
            # Add error code if provided
            if self.config.get("error_code"):
                embed.add_field(
                    name="Error Code", 
                    value=f"`{self.config['error_code']}`",
                    inline=False
                )
            
            # Add footer if provided
            if self.config.get("footer"):
                embed.set_footer(text=self.config["footer"])
            else:
                # Default footer with timestamp
                embed.set_footer(text="Contact an administrator if this error persists")
                embed.timestamp = discord.utils.utcnow()
                
            return embed
            
        except Exception as e:
            logger.error(f"Error building error embed: {str(e)}")
            # Return a minimal embed if we had an error building the proper one
            return discord.Embed(
                title="Error Display Failed",
                description="An error occurred while trying to display the error message.",
                color=discord.Color.dark_red()
            )
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'ErrorEmbed':
        """Create an ErrorEmbed from serialized data.
        
        Args:
            data: The serialized data
            
        Returns:
            The created ErrorEmbed instance
        """
        return cls(config=data.get("config", {})) 