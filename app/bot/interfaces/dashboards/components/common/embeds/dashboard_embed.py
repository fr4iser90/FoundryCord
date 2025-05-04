"""Dashboard embed component for displaying dashboard content."""

import nextcord
from typing import Optional, Dict, Any, ClassVar, List, Union, TYPE_CHECKING

from app.shared.interface.logging.api import get_bot_logger
from app.bot.interfaces.dashboards.components.base_component import BaseComponent

# Use TYPE_CHECKING to avoid circular import during runtime
if TYPE_CHECKING:
    from app.bot.infrastructure.startup.bot import FoundryCord

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
        # --- DETAILED LOGGING START ---
        instance_id = self.config.get('instance_id', 'UNKNOWN_INSTANCE')
        logger.info(f"[Embed Build - {instance_id}] STARTING BUILD. Full self.config: {self.config}")
        # --- DETAILED LOGGING END ---
        try:
            # Use self.config which now holds the merged values
            # --- DETAILED LOGGING ---
            title = self.config.get("title", "Default Title")
            description = self.config.get("description", "")
            color_value = self.config.get("color", nextcord.Color.blurple().value)
            logger.info(f"[Embed Build - {instance_id}] Creating base embed with Title='{title}', Desc='{description[:50]}...', Color={color_value}")
            # --- DETAILED LOGGING END ---
            embed = nextcord.Embed(
                title=title, # Use merged config
                description=description, # Use merged config
                color=color_value # Use merged config
            )

            # Add fields if provided in merged config
            fields = self.config.get("fields", [])
            # --- DETAILED LOGGING ---
            logger.info(f"[Embed Build - {instance_id}] Processing {len(fields) if isinstance(fields, list) else 0} fields...")
            # --- DETAILED LOGGING END ---
            if isinstance(fields, list):
                 for i, field in enumerate(fields):
                     if isinstance(field, dict):
                           # --- DETAILED LOGGING ---
                           field_name = field.get("name", "\\u200b")
                           field_value = field.get("value", "")
                           field_inline = field.get("inline", True)
                           logger.info(f"[Embed Build - {instance_id}] Adding Field {i+1}: Name='{field_name}', Value='{field_value[:50]}...', Inline={field_inline}")
                           # --- DETAILED LOGGING END ---
                           embed.add_field(
                               name=field_name,
                               value=field_value,
                               inline=field_inline
                           )
                     else:
                         # --- DETAILED LOGGING ---
                         logger.warning(f"[Embed Build - {instance_id}] Field {i+1} in config is not a dict: {field}. Skipping.")
                         # --- DETAILED LOGGING END ---
            else:
                 # --- DETAILED LOGGING ---
                 logger.warning(f"[Embed Build - {instance_id}] 'fields' in config is not a list: {fields}. Skipping fields.")
                 # --- DETAILED LOGGING END ---


            # Set image if provided
            image_url = self.config.get("image_url")
            if image_url:
                # --- DETAILED LOGGING ---
                logger.info(f"[Embed Build - {instance_id}] Setting Image URL: {image_url}")
                # --- DETAILED LOGGING END ---
                embed.set_image(url=image_url)

            # Set thumbnail if provided
            thumbnail_url = self.config.get("thumbnail_url")
            if thumbnail_url:
                # --- DETAILED LOGGING ---
                logger.info(f"[Embed Build - {instance_id}] Setting Thumbnail URL: {thumbnail_url}")
                # --- DETAILED LOGGING END ---
                embed.set_thumbnail(url=thumbnail_url)

            # Add footer if provided
            footer_data = self.config.get("footer")
            if isinstance(footer_data, dict):
                 # --- DETAILED LOGGING ---
                 footer_text = footer_data.get("text", "")
                 footer_icon_url = footer_data.get("icon_url")
                 logger.info(f"[Embed Build - {instance_id}] Setting Footer: Text='{footer_text}', Icon='{footer_icon_url}'")
                 # --- DETAILED LOGGING END ---
                 embed.set_footer(
                     text=footer_text,
                     icon_url=footer_icon_url
                 )
            elif isinstance(footer_data, str): # Handle simple string footer
                 # --- DETAILED LOGGING ---
                 logger.info(f"[Embed Build - {instance_id}] Setting Footer (string): Text='{footer_data}'")
                 # --- DETAILED LOGGING END ---
                 embed.set_footer(text=footer_data)
            else:
                 # --- DETAILED LOGGING ---
                 if footer_data is not None:
                    logger.info(f"[Embed Build - {instance_id}] No valid footer data found in config (Type: {type(footer_data)}). Skipping footer.")
                 # --- DETAILED LOGGING END ---


            # Add author if provided
            author_data = self.config.get("author")
            if isinstance(author_data, dict):
                  # --- DETAILED LOGGING ---
                  author_name = author_data.get("name", "")
                  author_url = author_data.get("url")
                  author_icon_url = author_data.get("icon_url")
                  logger.info(f"[Embed Build - {instance_id}] Setting Author: Name='{author_name}', URL='{author_url}', Icon='{author_icon_url}'")
                  # --- DETAILED LOGGING END ---
                  embed.set_author(
                     name=author_name,
                     url=author_url,
                     icon_url=author_icon_url
                  )
            elif isinstance(author_data, str): # Handle simple string author name
                 # --- DETAILED LOGGING ---
                 logger.info(f"[Embed Build - {instance_id}] Setting Author (string): Name='{author_data}'")
                 # --- DETAILED LOGGING END ---
                 embed.set_author(name=author_data)
            else:
                 # --- DETAILED LOGGING ---
                 if author_data is not None:
                     logger.info(f"[Embed Build - {instance_id}] No valid author data found in config (Type: {type(author_data)}). Skipping author.")
                 # --- DETAILED LOGGING END ---

            # Add timestamp if configured
            if self.config.get("timestamp", True):
                  # --- DETAILED LOGGING ---
                  logger.info(f"[Embed Build - {instance_id}] Setting Timestamp.")
                  # --- DETAILED LOGGING END ---
                  embed.timestamp = nextcord.utils.utcnow()

            # --- DETAILED LOGGING ---
            logger.info(f"[Embed Build - {instance_id}] BUILD SUCCESSFUL. Returning embed.")
            # --- DETAILED LOGGING END ---
            return embed

        except Exception as e:
            # --- DETAILED LOGGING ---
            logger.error(f"[Embed Build - {instance_id}] BUILD FAILED with exception: {str(e)}", exc_info=True)
            # --- DETAILED LOGGING END ---
            # Return a minimal embed if we had an error building the proper one
            return nextcord.Embed(
                 title="Error Building Embed",
                 description=f"An error occurred while building this embed ({instance_id}).",
                 color=nextcord.Color.red()
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