"""Base component for dashboard UI elements."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Awaitable, Union, List, ClassVar, TYPE_CHECKING
import nextcord
import copy

from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

if TYPE_CHECKING:
    from app.bot.core.main import FoundryCord # For type hinting bot

class BaseComponent(ABC):
    """Base class for all dashboard components.
    
    This abstract class provides the foundation for all UI components
    in the dashboard system, ensuring a consistent interface and behavior.
    """
    
    # Class variables that should be overridden by subclasses
    COMPONENT_TYPE: ClassVar[str] = "base"
    
    def __init__(self, bot: 'FoundryCord', instance_config: Dict[str, Any]):
        """
        Initialize the component using instance config and base definition from registry.

        Args:
            bot: The bot instance (needed to access ComponentRegistry).
            instance_config: Configuration specific to this instance, MUST contain
                             'instance_id' and 'component_key'. May contain 'settings'.
        """
        self.bot = bot
        self.config: Dict[str, Any] = {} # Final merged config

        if not bot:
            logger.error(f"{self.__class__.__name__} initialized without bot instance. Cannot fetch base definition.")
            # Initialize with instance config only as fallback? Or raise error?
            # For now, let's log error and continue with potentially incomplete config.
            self.config = copy.deepcopy(instance_config)
            return # Cannot proceed further without bot

        component_key = instance_config.get('component_key')
        instance_id = instance_config.get('instance_id')
        instance_settings = instance_config.get('settings', {})

        if not component_key or not instance_id:
            logger.error(f"{self.__class__.__name__} initialized with invalid instance_config (missing key or id): {instance_config}")
            self.config = copy.deepcopy(instance_config) # Store what we got
            return # Cannot proceed

        # 1. Get base definition from registry
        base_definition_dict = {}
        if bot.component_registry:
            # get_definition_by_key returns the wrapper dict, need ['definition']
            base_definition_wrapper = bot.component_registry.get_definition_by_key(component_key)
            if base_definition_wrapper and 'definition' in base_definition_wrapper:
                 # Make a deep copy to avoid modifying the cached definition
                 base_definition_dict = copy.deepcopy(base_definition_wrapper['definition'])
            else:
                 logger.warning(f"Base definition not found or invalid in registry for key '{component_key}'. Component might use defaults.")
        else:
            logger.error("ComponentRegistry not found on bot instance during BaseComponent init.")

        # 2. Merge: Base Definition < Instance Settings
        # Start with the base definition
        merged_config = base_definition_dict
        # Update/Override with instance settings
        if isinstance(instance_settings, dict):
            merged_config.update(instance_settings)
        else:
             logger.warning(f"Instance settings for {instance_id} are not a dictionary: {instance_settings}. Ignoring.")

        # 3. Store final config and essential instance info
        self.config = merged_config
        # Ensure instance_id and component_key are directly accessible in the final config
        self.config['instance_id'] = instance_id
        self.config['component_key'] = component_key
        # Ensure core attributes like visible/enabled exist (can default to True)
        self.config.setdefault('visible', True)
        self.config.setdefault('enabled', True)


        # logger.debug(f"Initialized {self.__class__.__name__} component '{instance_id}'. Final config: {self.config}") # Optional detailed log
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update the component configuration. (Use with caution)"""
        self.config.update(new_config)
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current component configuration."""
        return copy.deepcopy(self.config)
    
    def is_visible(self) -> bool:
        """Check if the component is visible."""
        return self.config.get("visible", True)
    
    def set_visible(self, visible: bool) -> None:
        """Set component visibility."""
        self.config["visible"] = visible
    
    def is_enabled(self) -> bool:
        """Check if the component is enabled."""
        return self.config.get("enabled", True)
    
    def set_enabled(self, enabled: bool) -> None:
        """Set component enabled state."""
        self.config["enabled"] = enabled
    
    @abstractmethod
    def build(self) -> Any:
        """Build and return the component object.
        
        This method must be implemented by subclasses to construct the
        actual Discord component (embed, button, etc).
        
        Returns:
            The built component
        """
        pass
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize the component for storage.
        
        Returns:
            Serialized component data
        """
        return {
            "component_type": self.COMPONENT_TYPE,
            "config": self.get_config()
        }
    
    @classmethod
    @abstractmethod
    def deserialize(cls, data: Dict[str, Any], bot=None) -> 'BaseComponent':
        """Create a component from serialized data.
        
        This method should be implemented by subclasses to properly
        instantiate the specific component type.
        
        Args:
            data: Serialized component data
            
        Returns:
            Instantiated component
        """
        raise NotImplementedError("Subclasses must implement deserialize method")

class DashboardComponent(ABC):
    """Base class for dashboard components."""
    
    def __init__(self, bot, config: Dict[str, Any]):
        self.bot = bot
        self.config = config
        self.id = config.get("id")
        
    @abstractmethod
    async def render_to_embed(self, embed: nextcord.Embed, data: Any, config: Dict[str, Any]) -> None:
        """Render component to an embed."""
        pass
        
    @abstractmethod
    async def create_ui_component(self, view: nextcord.ui.View, data: Any, 
                                 config: Dict[str, Any], dashboard_id: str) -> Optional[nextcord.ui.Item]:
        """Create UI component for interactive view."""
        pass
        
    @abstractmethod
    async def on_interaction(self, interaction: nextcord.Interaction, data: Any, 
                           config: Dict[str, Any], dashboard_id: str) -> None:
        """Handle interaction with this component."""
        pass 