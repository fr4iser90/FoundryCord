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
    # This function now only needs to handle dict data, 
    # as list data is handled directly in the build method.
    if not template_string:
        return ""
    try:
        formatted_string = template_string
        if data and isinstance(data, dict): # Ensure data is a dictionary
            for key, value in data.items():
                placeholder = f'{{{{{key}}}}}' 
                replacement_value = str(value) # Simple string conversion for dict values
                formatted_string = formatted_string.replace(placeholder, replacement_value)
        
        return formatted_string
    except Exception as e:
        logger.error(f"Error formatting string '{template_string[:50]}...' with dict data: {e}", exc_info=True)
        return template_string 

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
    
    def build(self, data: Optional[Union[Dict[str, Any], List[Any]]] = None) -> nextcord.Embed: # Allow data to be list or dict
        """Build and return the Discord embed object using the merged config and provided data."""
        instance_id = self.config.get('instance_id', 'UNKNOWN_INSTANCE')
        # Keep log minimal
        data_type_log = type(data).__name__ if data is not None else 'None'
        logger.debug(f"[{instance_id}] Building embed with data type: {data_type_log}") 
        try:
             title = self.config.get("title", "Default Title")
             # Title/Description usually don't use list data directly
             formatted_title = format_string(title, data if isinstance(data, dict) else {}) 
             description = self.config.get("description", "")
             formatted_description = format_string(description, data if isinstance(data, dict) else {})
             color_value = self.config.get("color", nextcord.Color.blurple().value)
             embed = nextcord.Embed(
                 title=formatted_title, 
                 description=formatted_description, 
                 color=color_value 
             )

             fields = self.config.get("fields", [])
             if isinstance(fields, list):
                  for i, field in enumerate(fields):
                      if isinstance(field, dict):
                            field_name = field.get("name", "\u200b")
                            field_value_template = field.get("value", "") # The template like {{projects}} or {{hostname}}
                            field_inline = field.get("inline", True)
                            
                            formatted_field_value = "" # Default value

                            # --- START SPECIAL LIST HANDLING ---
                            # Check if data is a list AND the template looks like a simple placeholder {{key}}
                            if isinstance(data, list) and field_value_template.startswith("{{") and field_value_template.endswith("}}") and field_value_template.count('{') == 2: 
                                logger.debug(f"[{instance_id}] Field '{field_name}' processing as list data.")
                                formatted_field_value = format_list_to_string(data) # Format the list directly
                            # --- END SPECIAL LIST HANDLING ---
                            
                            # --- ELSE: Handle as dictionary (or if template is complex) ---
                            elif isinstance(data, dict):
                                logger.debug(f"[{instance_id}] Field '{field_name}' processing as dict data using format_string.")
                                # --- START: Python formatting for 'projects' list --- 
                                if field_value_template == '{{projects}}' and 'projects' in data and isinstance(data.get('projects'), list):
                                    project_list = data.get('projects', [])
                                    if project_list:
                                        formatted_lines = [f"- {p.get('name', 'N/A')} ({p.get('status', 'N/A')})" for p in project_list]
                                        formatted_field_value = "\\n".join(formatted_lines)
                                    else:
                                        formatted_field_value = "No projects found."
                                    logger.debug(f"[{instance_id}] Field '{field_name}' formatted as project list: {formatted_field_value[:50]}...")
                                # --- START: Python formatting for 'server_status_summary' ---
                                elif field_value_template == '{{server_status_summary}}' and 'services' in data and isinstance(data.get('services'), dict):
                                    service_statuses = data.get('services', {})
                                    online_count = 0
                                    offline_count = 0
                                    other_count = 0
                                    for status in service_statuses.values():
                                        # Basic check, might need refinement based on actual status strings
                                        if isinstance(status, str):
                                            if 'online' in status.lower():
                                                online_count += 1
                                            elif 'offline' in status.lower():
                                                offline_count += 1
                                            else:
                                                other_count += 1
                                        else: # Handle unexpected status types
                                            other_count += 1
                                            
                                    summary_parts = []
                                    if online_count > 0:
                                        summary_parts.append(f"Online: {online_count}")
                                    if offline_count > 0:
                                        summary_parts.append(f"Offline: {offline_count}")
                                    if other_count > 0:
                                        summary_parts.append(f"Other: {other_count}")
                                    
                                    formatted_field_value = " | ".join(summary_parts) if summary_parts else "N/A"
                                    logger.debug(f"[{instance_id}] Field '{field_name}' formatted as server status summary: {formatted_field_value}")
                                else:
                                    # --- ELSE: Fallback to generic format_string (CORRECTED CALL) ---
                                    try:
                                        formatted_field_value = format_string(field_value_template, data)
                                        logger.debug(f"[{instance_id}] Field '{field_name}' processed using format_string. Result: {formatted_field_value[:100]}...") # Log first 100 chars
                                    except Exception as fmt_e:
                                        logger.warning(f"[{instance_id}] Failed to format field '{field_name}' with template '{field_value_template}' using format_string: {fmt_e}", exc_info=False)
                                        formatted_field_value = f"Error formatting field '{field_name}'"
                                # --- END: Python formatting for 'projects' list ---
                            # --- END ELSE ---
                            
                            else: # Fallback if data is not dict or list, or if template didn't match list pattern
                                 logger.debug(f"[{instance_id}] Field '{field_name}' using template directly as data type ('{data_type_log}') was unexpected.")
                                 formatted_field_value = field_value_template # Use template string as fallback

                            embed.add_field(
                                name=format_string(field_name, data if isinstance(data, dict) else {}), # Format name only with dict data
                                value=formatted_field_value,
                                inline=field_inline
                            )
                      else:
                          logger.warning(f"[{instance_id}] Field {i+1} in config is not a dict: {field}. Skipping.")
             else:
                  logger.warning(f"[{instance_id}] 'fields' in config is not a list: {fields}. Skipping fields.")
 
             # Set image if provided
             image_url = self.config.get("image_url")
             if image_url:
                 embed.set_image(url=format_string(image_url, data if isinstance(data, dict) else {}))
 
             # Set thumbnail if provided
             thumbnail_url = self.config.get("thumbnail_url")
             if thumbnail_url:
                 embed.set_thumbnail(url=format_string(thumbnail_url, data if isinstance(data, dict) else {}))
 
             # Add footer if provided
             footer_data = self.config.get("footer")
             if isinstance(footer_data, dict):
                  footer_text = footer_data.get("text", "")
                  formatted_footer_text = format_string(footer_text, data if isinstance(data, dict) else {})
                  footer_icon_url = footer_data.get("icon_url")
                  embed.set_footer(
                      text=formatted_footer_text,
                      icon_url=format_string(footer_icon_url, data if isinstance(data, dict) else {})
                  )
             elif isinstance(footer_data, str): 
                  embed.set_footer(text=format_string(footer_data, data if isinstance(data, dict) else {}))
 
             # Add author if provided
             author_data = self.config.get("author")
             if isinstance(author_data, dict):
                   author_name = author_data.get("name", "")
                   formatted_author_name = format_string(author_name, data if isinstance(data, dict) else {})
                   author_url = author_data.get("url")
                   author_icon_url = author_data.get("icon_url")
                   embed.set_author(
                       name=formatted_author_name,
                       url=format_string(author_url, data if isinstance(data, dict) else {}),
                       icon_url=format_string(author_icon_url, data if isinstance(data, dict) else {})
                   )
             elif isinstance(author_data, str): 
                  embed.set_author(name=format_string(author_data, data if isinstance(data, dict) else {}))
 
             # Add timestamp if configured
             if self.config.get("timestamp", True):
                   embed.timestamp = nextcord.utils.utcnow()
 
             logger.debug(f"[{instance_id}] Embed build successful.")
             return embed
 
        except Exception as e:
             logger.error(f"[{instance_id}] Embed build FAILED: {str(e)}", exc_info=True)
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