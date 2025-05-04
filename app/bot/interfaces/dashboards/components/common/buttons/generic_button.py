import nextcord
from typing import Optional, Dict, Any, ClassVar
from app.shared.interface.logging.api import get_bot_logger
from app.bot.interfaces.dashboards.components.base_component import BaseComponent

logger = get_bot_logger()

class GenericButtonComponent(BaseComponent):
    """
    Generic Button Component that creates a nextcord.ui.Button based on DB config.
    Inherits from BaseComponent for registry compatibility.
    """
    COMPONENT_TYPE: ClassVar[str] = "button" # Matches the type string from DB

    def __init__(self, bot, config: Optional[Dict[str, Any]] = None):
        """
        Initializes the generic button component.

        Args:
            bot: The bot instance.
            config: Configuration dictionary from the database for this specific button instance.
                    Expected keys: 'instance_id', 'component_key', 'label', 'style', 'emoji', 'row', 'disabled', 'custom_id' (optional, defaults to instance_id)
        """
        self.bot = bot # Store bot instance if needed for callbacks later
        default_config = {
            "label": "Button",
            "style": "primary",
            "emoji": None,
            "row": 0,
            "disabled": False,
            "visible": True, # Assuming buttons are components that need visibility checks
            "enabled": True,
            "custom_id": None # Will be set from instance_id if not provided
        }
        # Initialize BaseComponent AFTER setting self.bot
        super().__init__(config=config, default_config=default_config)

        # Use instance_id as default custom_id for interaction tracking
        if self.config.get("custom_id") is None:
            self.config["custom_id"] = self.config.get("instance_id")

        logger.debug(f"Initialized GenericButtonComponent for instance_id: {self.config.get('instance_id')}")


    def build(self) -> Optional[nextcord.ui.Button]:
        """
        Builds the nextcord.ui.Button instance based on the configuration.
        This method might not be directly called if add_to_view is used,
        but provides a way to get the raw button object.
        """
        if not self.is_visible():
            return None

        try:
            button_style_str = self.config.get("style", "primary").lower()
            button_style = getattr(nextcord.ButtonStyle, button_style_str, nextcord.ButtonStyle.primary)

            button = nextcord.ui.Button(
                label=self.config.get("label"),
                custom_id=self.config.get("custom_id"), # Should default to instance_id
                style=button_style,
                emoji=self.config.get("emoji"),
                row=self.config.get("row", 0),
                disabled=not self.is_enabled() # Use is_enabled() for disabling
            )
            return button
        except Exception as e:
            logger.error(f"Error building GenericButtonComponent (instance_id: {self.config.get('instance_id')}): {e}", exc_info=True)
            return None

    async def add_to_view(self, view: nextcord.ui.View, data: Dict[str, Any], component_config: Dict[str, Any]):
        """Adds the button to the provided view if visible and enabled."""
        # Update config just in case it changed
        self.update_config(component_config)

        if not self.is_visible():
            logger.debug(f"GenericButtonComponent (instance_id: {self.config.get('instance_id')}) is not visible. Skipping add.")
            return

        button_instance = self.build()
        if button_instance:
            # The callback logic will be handled centrally by DashboardController
            # using the custom_id (which defaults to instance_id).
            # We don't need to assign a callback here.
            view.add_item(button_instance)
            logger.debug(f"Added GenericButtonComponent (instance_id: {self.config.get('instance_id')}) to view.")
        else:
            logger.warning(f"Failed to build GenericButtonComponent (instance_id: {self.config.get('instance_id')}). Not adding to view.")


    # --- BaseComponent abstract methods ---
    @classmethod
    def deserialize(cls, data: Dict[str, Any], bot=None) -> 'GenericButtonComponent':
        """Deserializes data into a GenericButtonComponent instance."""
        # Requires bot instance, which might not be available during pure deserialization
        # Consider how bot dependency is handled if deserializing outside controller context
        if not bot:
             logger.warning("Deserializing GenericButtonComponent without bot instance.")
        return cls(bot=bot, config=data.get("config", {}))

    # render_to_embed is not typically needed for buttons
    async def render_to_embed(self, embed: nextcord.Embed, data: Any, config: Dict[str, Any]):
        """Buttons usually don't render to embeds."""
        pass

    # on_interaction is handled by DashboardController based on custom_id
    async def on_interaction(self, interaction: nextcord.Interaction, data: Any, config: Dict[str, Any], dashboard_id: str):
        """Interaction logic is handled by the DashboardController."""
        logger.warning("GenericButtonComponent.on_interaction called directly, but should be handled by DashboardController.")
        pass 