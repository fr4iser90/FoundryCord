"""Dashboard embed component for displaying dashboard content."""

import nextcord
from typing import Optional, Dict, Any, ClassVar, List, Union, TYPE_CHECKING

from app.shared.interface.logging.api import get_bot_logger
from app.bot.interfaces.dashboards.components.base_component import BaseComponent

if TYPE_CHECKING:
    from app.bot.core.main import FoundryCord

logger = get_bot_logger()

class DashboardEmbed(BaseComponent):
    """Main dashboard embed for displaying dashboard content."""
    
    # Class variables
    COMPONENT_TYPE: ClassVar[str] = "dashboard_embed"
    
    def __init__(self, bot: 'FoundryCord', instance_config: Dict[str, Any]):
        """
        Initialize the dashboard embed.

        Args:
            bot: The bot instance.
            instance_config: Configuration specific to this instance from the dashboard layout.
                             MUST contain 'instance_id' and 'component_key'.
        """
        # Call the updated BaseComponent __init__ which handles the config merging
        super().__init__(bot=bot, instance_config=instance_config)
        # No component-specific init logic needed here anymore, config is merged in base.
        # logger.debug(f"Initialized DashboardEmbed component for instance_id: {self.config.get('instance_id')}")
    
    def build(self) -> nextcord.Embed:
        """Build and return the Discord embed object using the merged config."""
        try:
            # Use self.config which now holds the merged values
            embed = nextcord.Embed(
                title=self.config.get("title", "Default Title"), # Use merged config
                description=self.config.get("description", ""), # Use merged config
                color=self.config.get("color", nextcord.Color.blurple().value) # Use merged config
            )

            # Add fields if provided in merged config
            fields = self.config.get("fields", [])
            if isinstance(fields, list):
                for field in fields:
                     if isinstance(field, dict):
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
            footer_data = self.config.get("footer")
            if isinstance(footer_data, dict):
                embed.set_footer(
                    text=footer_data.get("text", ""),
                    icon_url=footer_data.get("icon_url")
                )
            elif isinstance(footer_data, str): # Handle simple string footer
                 embed.set_footer(text=footer_data)

            # Add author if provided
            author_data = self.config.get("author")
            if isinstance(author_data, dict):
                 embed.set_author(
                    name=author_data.get("name", ""),
                    url=author_data.get("url"),
                    icon_url=author_data.get("icon_url")
                 )
            elif isinstance(author_data, str): # Handle simple string author name
                 embed.set_author(name=author_data)

            # Add timestamp if configured
            if self.config.get("timestamp", True):
                 embed.timestamp = nextcord.utils.utcnow()

            return embed

        except Exception as e:
            logger.error(f"Error building dashboard embed (Instance: {self.config.get('instance_id')}): {str(e)}")
            # Return a minimal embed if we had an error building the proper one
            return nextcord.Embed(
                title="Dashboard Error",
                description="An error occurred while building this dashboard embed.",
                color=nextcord.Color.dark_gray()
            )

    # --- Field methods now directly modify self.config ---
    def add_field(self, name: str, value: str, inline: bool = True) -> None:
        """Add a field to the embed configuration."""
        if "fields" not in self.config or not isinstance(self.config["fields"], list):
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
    def deserialize(cls, data: Dict[str, Any], bot=None) -> 'DashboardEmbed':
        """Create a DashboardEmbed from serialized data."""
        # Assumes 'data' contains the 'instance_config' structure
        if not bot:
             logger.warning("Deserializing DashboardEmbed without bot instance.")
        return cls(bot=bot, instance_config=data)

    async def render_to_embed(self, embed: nextcord.Embed, data: Any, config: Dict[str, Any]):
         # This method might become redundant if 'build' does everything based on self.config
         # For now, just log a warning if called directly.
         logger.warning("DashboardEmbed.render_to_embed called directly. Logic should be in build().")
         pass