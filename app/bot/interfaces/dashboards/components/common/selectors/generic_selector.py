import nextcord
from typing import Optional, Dict, Any, List, ClassVar
from abc import ABC, abstractmethod
from typing import Coroutine

from app.shared.interfaces.logging.api import get_bot_logger
from app.bot.interfaces.dashboards.components.base_component import BaseComponent

logger = get_bot_logger()

class GenericSelectorComponent(BaseComponent):
    """
    Generic Selector Component (Dropdown Menu) based on DB config.
    """
    COMPONENT_TYPE: ClassVar[str] = "selector" # Matches the type string from DB

    def __init__(self, bot, instance_config: Dict[str, Any]):
        """
        Initializes the generic selector component.

        Args:
            bot: The bot instance.
            instance_config: Configuration specific to this instance from the dashboard layout.
                             MUST contain 'instance_id' and 'component_key'.
        """
        # Call the updated BaseComponent __init__ which handles the config merging
        super().__init__(bot=bot, instance_config=instance_config)

        # Default custom_id logic, using the merged self.config
        # Important for interaction tracking in DashboardController
        if self.config.get("custom_id") is None:
             self.config["custom_id"] = self.config.get("instance_id")

        logger.debug(f"Initialized GenericSelectorComponent for instance_id: {self.config.get('instance_id')}")

    def build(self) -> Optional[nextcord.ui.Select]:
        """ Builds the nextcord.ui.Select instance based on the merged configuration. """
        if not self.is_visible():
            return None

        try:
            instance_id = self.config.get('instance_id', 'UNKNOWN_INSTANCE')
            logger.debug(f"[DIAGNOSTIC Selector Build - {instance_id}] Building selector with self.config: {self.config}")

            options_data = self.config.get("options", [])
            select_options: List[nextcord.SelectOption] = []

            if not isinstance(options_data, list):
                logger.error(f"[Selector Build - {instance_id}] 'options' in config is not a list: {options_data}. Cannot build selector.")
                return None

            for option_dict in options_data:
                if not isinstance(option_dict, dict):
                    logger.warning(f"[Selector Build - {instance_id}] Skipping invalid option (not a dict): {option_dict}")
                    continue
                
                label = option_dict.get("label")
                value = option_dict.get("value")
                if not label or not value:
                     logger.warning(f"[Selector Build - {instance_id}] Skipping option with missing label or value: {option_dict}")
                     continue

                select_options.append(
                    nextcord.SelectOption(
                        label=str(label),
                        value=str(value),
                        description=option_dict.get("description"),
                        emoji=option_dict.get("emoji"),
                        default=option_dict.get("default", False)
                    )
                )
                
            if not select_options:
                 logger.warning(f"[Selector Build - {instance_id}] No valid options found after processing. Cannot build selector.")
                 return None

            select_menu = nextcord.ui.Select(
                custom_id=self.config.get("custom_id"), # Should default to instance_id
                placeholder=self.config.get("placeholder", "Select an option..."),
                min_values=self.config.get("min_values", 1),
                max_values=self.config.get("max_values", 1),
                options=select_options,
                row=self.config.get("row"), # Let nextcord handle default if None
                disabled=not self.is_enabled()
            )
            
            logger.debug(f"[Selector Build - {instance_id}] Successfully built selector.")
            return select_menu

        except Exception as e:
            logger.error(f"Error building GenericSelectorComponent (instance_id: {instance_id}): {e}", exc_info=True)
            return None

    async def add_to_view(self, view: nextcord.ui.View, data: Dict[str, Any], component_config: Dict[str, Any]):
         """Adds the selector to the provided view if visible and enabled."""
         if not self.is_visible():
             # logger.debug(f"GenericSelectorComponent (instance_id: {self.config.get('instance_id')}) is not visible. Skipping add.")
             return

         selector_instance = self.build()
         if selector_instance:
             # The callback logic will be handled centrally by DashboardController
             # using the custom_id (which defaults to instance_id).
             view.add_item(selector_instance)
             # logger.debug(f"Added GenericSelectorComponent (instance_id: {self.config.get('instance_id')}) to view.")
         else:
             logger.warning(f"Failed to build GenericSelectorComponent (instance_id: {self.config.get('instance_id')}). Not adding to view.")

    # --- BaseComponent abstract methods ---
    @classmethod
    def deserialize(cls, data: Dict[str, Any], bot=None) -> 'GenericSelectorComponent':
        """Deserializes data into a GenericSelectorComponent instance."""
        # Assumes 'data' contains the 'instance_config' structure
        if not bot:
             logger.warning("Deserializing GenericSelectorComponent without bot instance.")
        # Pass bot and the data (assumed to be instance_config) to constructor
        return cls(bot=bot, instance_config=data)

    async def render_to_embed(self, embed: nextcord.Embed, data: Any, config: Dict[str, Any]):
        """Selectors do not render to embeds."""
        pass

    async def on_interaction(self, interaction: nextcord.Interaction, data: Any, config: Dict[str, Any], dashboard_id: str):
        """Interaction logic is handled by the DashboardController."""
        logger.warning("GenericSelectorComponent.on_interaction called directly, but should be handled by DashboardController.")
        pass
