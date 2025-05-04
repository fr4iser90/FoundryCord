"""Dashboard embed component for displaying dashboard content."""

import nextcord
from typing import Optional, Dict, Any, ClassVar, List, Union, TYPE_CHECKING

from app.shared.interface.logging.api import get_bot_logger
from app.bot.interfaces.dashboards.components.base_component import BaseComponent

# Use TYPE_CHECKING to avoid circular import during runtime
if TYPE_CHECKING:
    from app.bot.infrastructure.startup.bot import FoundryCord

logger = get_bot_logger()

def format_list_to_string(items: List[Any]) -> str:
    """Formats a list into a bulleted string representation."""
    if not items:
        return "*Keine Einträge vorhanden*"
    
    formatted_items = []
    for item in items:
        # Attempt to get a meaningful representation
        if hasattr(item, 'name'):
            formatted_items.append(f"- {getattr(item, 'name')}")
        elif hasattr(item, 'title'):
            formatted_items.append(f"- {getattr(item, 'title')}")
        elif isinstance(item, str):
            formatted_items.append(f"- {item}")
        elif isinstance(item, (int, float)):
             formatted_items.append(f"- {str(item)}")
        else:
            # Fallback to generic string representation
            try:
                 item_str = str(item)
                 # Optional: Truncate long representations
                 if len(item_str) > 50:
                      item_str = item_str[:47] + "..."
                 formatted_items.append(f"- {item_str}")
            except Exception:
                 formatted_items.append("- *[Fehler bei Darstellung]*")
            
    return "\n".join(formatted_items)

def format_string(template_string: Optional[str], data: Dict[str, Any]) -> str:
    if not template_string:
        return ""
    try:
        formatted_string = template_string
        if data: # Only attempt replacements if data is provided
            for key, value in data.items():
                placeholder = f'{{{{{key}}}}}' # Construct the placeholder e.g., {{projects}}
                
                # --- MODIFICATION START: Handle lists --- 
                if isinstance(value, list):
                    replacement_value = format_list_to_string(value)
                else:
                    replacement_value = str(value)
                # --- MODIFICATION END --- 
                
                # Replace all occurrences
                formatted_string = formatted_string.replace(placeholder, replacement_value)
        
        return formatted_string
    except Exception as e:
        # Log general errors but still return original template or partial
        logger.error(f"Error formatting string '{template_string[:50]}...': {e}", exc_info=True)
        # Return partially formatted or original template on error
        return template_string # Or potentially formatted_string if partial is okay

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
    
    def build(self, data: Optional[Dict[str, Any]] = None) -> nextcord.Embed:
        """Build and return the Discord embed object using the merged config and provided data."""
         # --- DETAILED LOGGING START ---
        instance_id = self.config.get('instance_id', 'UNKNOWN_INSTANCE')
        logger.debug(f"[{instance_id}] Building embed with data keys: {list(data.keys()) if data else 'None'}") # Simplified log
        try:
             # Use self.config which now holds the merged values
             # --- DETAILED LOGGING ---
             title = self.config.get("title", "Default Title")
             formatted_title = format_string(title, data or {})
             description = self.config.get("description", "")
             formatted_description = format_string(description, data or {})
             color_value = self.config.get("color", nextcord.Color.blurple().value)
             # Removed detailed base embed creation log
             embed = nextcord.Embed(
                 title=formatted_title, # Use formatted string
                 description=formatted_description, # Use formatted string
                 color=color_value # Use merged config
             )

             # Add fields if provided in merged config
             fields = self.config.get("fields", [])
             # --- DETAILED LOGGING ---
             # Removed field processing count log
             if isinstance(fields, list):
                  for i, field in enumerate(fields):
                      if isinstance(field, dict):
                            # --- DETAILED LOGGING ---
                            field_name = field.get("name", "\u200b")
                            formatted_field_name = format_string(field_name, data or {})
                            field_value = field.get("value", "")
                            formatted_field_value = format_string(field_value, data or {})
                            field_inline = field.get("inline", True)
                            # Removed individual field add log
                            embed.add_field(
                                name=formatted_field_name,
                                value=formatted_field_value,
                                inline=field_inline
                            )
                      else:
                          # --- DETAILED LOGGING ---
                          logger.warning(f"[{instance_id}] Field {i+1} in config is not a dict: {field}. Skipping.")
             else:
                  # --- DETAILED LOGGING ---
                  logger.warning(f"[{instance_id}] 'fields' in config is not a list: {fields}. Skipping fields.")
 
 
             # Set image if provided
             image_url = self.config.get("image_url")
             if image_url:
                 # --- DETAILED LOGGING ---
                 # Removed image set log
                 embed.set_image(url=image_url)
 
             # Set thumbnail if provided
             thumbnail_url = self.config.get("thumbnail_url")
             if thumbnail_url:
                 # --- DETAILED LOGGING ---
                 # Removed thumbnail set log
                 embed.set_thumbnail(url=thumbnail_url)
 
             # Add footer if provided
             footer_data = self.config.get("footer")
             if isinstance(footer_data, dict):
                  # --- DETAILED LOGGING ---
                  footer_text = footer_data.get("text", "")
                  formatted_footer_text = format_string(footer_text, data or {})
                  footer_icon_url = footer_data.get("icon_url")
                  # Removed footer set log
                  embed.set_footer(
                      text=formatted_footer_text,
                      icon_url=footer_icon_url
                  )
             elif isinstance(footer_data, str): # Handle simple string footer
                  # --- DETAILED LOGGING ---
                  # Removed footer set log (string)
                  embed.set_footer(text=footer_data)
             else:
                  # --- DETAILED LOGGING ---
                  if footer_data is not None:
                     logger.warning(f"[{instance_id}] Invalid footer data type in config: {type(footer_data)}. Skipping footer.")
 
 
             # Add author if provided
             author_data = self.config.get("author")
             if isinstance(author_data, dict):
                   # --- DETAILED LOGGING ---
                   author_name = author_data.get("name", "")
                   formatted_author_name = format_string(author_name, data or {})
                   author_url = author_data.get("url")
                   author_icon_url = author_data.get("icon_url")
                   # Removed author set log
                   embed.set_author(
                       name=formatted_author_name,
                       url=author_url,
                       icon_url=author_icon_url
                   )
             elif isinstance(author_data, str): # Handle simple string author name
                  # Removed author set log (string)
                  embed.set_author(name=author_data)
             else:
                  # --- DETAILED LOGGING ---
                  if author_data is not None:
                      logger.warning(f"[{instance_id}] Invalid author data type in config: {type(author_data)}. Skipping author.")
 
             # Add timestamp if configured
             if self.config.get("timestamp", True):
                   # --- DETAILED LOGGING ---
                   # Removed timestamp set log
                   embed.timestamp = nextcord.utils.utcnow()
 
             # --- DETAILED LOGGING ---
             logger.debug(f"[{instance_id}] Embed build successful.") # Changed to debug
             return embed
 
        except Exception as e:
             # --- DETAILED LOGGING ---
             logger.error(f"[{instance_id}] Embed build FAILED: {str(e)}", exc_info=True)
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