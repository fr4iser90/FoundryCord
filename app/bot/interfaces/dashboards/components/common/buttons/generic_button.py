import nextcord
from typing import Optional, Dict, Any, ClassVar
from app.shared.interfaces.logging.api import get_bot_logger
from app.bot.interfaces.dashboards.components.base_component import BaseComponent

logger = get_bot_logger()

class GenericButtonComponent(BaseComponent):
    """
    Generic Button Component that creates a nextcord.ui.Button based on DB config.
    Inherits from BaseComponent for registry compatibility.
    """
    COMPONENT_TYPE: ClassVar[str] = "button" # Matches the type string from DB

    def __init__(self, bot: 'FoundryCord', instance_config: Dict[str, Any]):
        """
        Initializes the generic button component.

        Args:
            bot: The bot instance.
            instance_config: Configuration specific to this instance from the dashboard layout.
                             MUST contain 'instance_id' and 'component_key'.
        """
        # Call the updated BaseComponent __init__ which handles the config merging
        super().__init__(bot=bot, instance_config=instance_config)

        # Default custom_id logic remains, using the merged self.config
        if self.config.get("custom_id") is None:
             self.config["custom_id"] = self.config.get("instance_id")

        logger.debug(f"Initialized GenericButtonComponent for instance_id: {self.config.get('instance_id')}")


    def build(self) -> Optional[nextcord.ui.Button]:
        """ Builds the nextcord.ui.Button instance based on the merged configuration. """
        if not self.is_visible():
            return None

        try:
            logger.debug(f"[DIAGNOSTIC Button Build] Building button with self.config: {self.config}") # Changed to debug
            

            # Now self.config should have the correct values merged from base definition
            button_style_str = self.config.get("style", "primary").lower() # Default still useful if base def is broken
            button_style = getattr(nextcord.ButtonStyle, button_style_str, nextcord.ButtonStyle.primary)

            button = nextcord.ui.Button(
                label=self.config.get("label", "Default Label"), # Use merged config
                custom_id=self.config.get("custom_id"),
                style=button_style,
                emoji=self.config.get("emoji"),
                row=self.config.get("row", 0),
                disabled=not self.is_enabled()
            )
            return button
        except Exception as e:
            logger.error(f"Error building GenericButtonComponent (instance_id: {self.config.get('instance_id')}): {e}", exc_info=True)
            return None

    async def add_to_view(self, view: nextcord.ui.View, data: Dict[str, Any], component_config: Dict[str, Any]):
         """Adds the button to the provided view if visible and enabled."""
         # instance_config was already processed in __init__. We just need to build.
         # Note: component_config passed here is the raw instance_config again,
         # maybe remove this parameter if __init__ handles everything? For now, ignore it.

         if not self.is_visible():
             # logger.debug(f"GenericButtonComponent (instance_id: {self.config.get('instance_id')}) is not visible. Skipping add.")
             return

         button_instance = self.build()
         if button_instance:
             view.add_item(button_instance)
             # logger.debug(f"Added GenericButtonComponent (instance_id: {self.config.get('instance_id')}) to view.")
         else:
             logger.warning(f"Failed to build GenericButtonComponent (instance_id: {self.config.get('instance_id')}). Not adding to view.")

    # --- BaseComponent abstract methods ---
    @classmethod
    def deserialize(cls, data: Dict[str, Any], bot=None) -> 'GenericButtonComponent':
        """Deserializes data into a GenericButtonComponent instance."""
        # Assumes 'data' contains the 'instance_config' structure
        if not bot:
             logger.warning("Deserializing GenericButtonComponent without bot instance.")
        # Pass bot and the data (assumed to be instance_config) to constructor
        return cls(bot=bot, instance_config=data)

    # render_to_embed is not typically needed for buttons
    async def render_to_embed(self, embed: nextcord.Embed, data: Any, config: Dict[str, Any]):
        """Buttons usually don't render to embeds."""
        pass

    # on_interaction is handled by DashboardController based on custom_id
    async def on_interaction(self, interaction: nextcord.Interaction, data: Any, config: Dict[str, Any], dashboard_id: str):
        """Interaction logic is handled by the DashboardController."""
        logger.warning("GenericButtonComponent.on_interaction called directly, but should be handled by DashboardController.")
        pass 