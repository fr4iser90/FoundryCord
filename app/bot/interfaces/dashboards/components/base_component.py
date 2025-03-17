"""Base component for dashboard UI elements."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Awaitable, Union, List, ClassVar
import nextcord
import copy

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class BaseComponent(ABC):
    """Base class for all dashboard components.
    
    This abstract class provides the foundation for all UI components
    in the dashboard system, ensuring a consistent interface and behavior.
    """
    
    # Class variables that should be overridden by subclasses
    COMPONENT_TYPE: ClassVar[str] = "base"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, default_config: Optional[Dict[str, Any]] = None):
        """Initialize the component with configuration.
        
        Args:
            config: Custom configuration for this component instance
            default_config: Default configuration values
        """
        # Create default configuration if not provided
        if default_config is None:
            default_config = {
                "visible": True,
                "enabled": True,
            }
            
        # Start with default configuration
        self.config = copy.deepcopy(default_config)
        
        # Override with custom configuration if provided
        if config:
            self.update_config(config)
            
        logger.debug(f"Initialized {self.__class__.__name__} component")
    
    @abstractmethod
    def build(self) -> Any:
        """Build and return the component object.
        
        This method must be implemented by subclasses to construct the
        actual Discord component (embed, button, etc).
        
        Returns:
            The built component
        """
        pass
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update the component configuration.
        
        Args:
            new_config: New configuration values to apply
        """
        self.config.update(new_config)
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current component configuration.
        
        Returns:
            The current configuration dictionary
        """
        return copy.deepcopy(self.config)
    
    def is_visible(self) -> bool:
        """Check if the component is visible.
        
        Returns:
            True if the component is visible, False otherwise
        """
        return self.config.get("visible", True)
    
    def set_visible(self, visible: bool) -> None:
        """Set component visibility.
        
        Args:
            visible: Whether the component should be visible
        """
        self.config["visible"] = visible
    
    def is_enabled(self) -> bool:
        """Check if the component is enabled.
        
        Returns:
            True if the component is enabled, False otherwise
        """
        return self.config.get("enabled", True)
    
    def set_enabled(self, enabled: bool) -> None:
        """Set component enabled state.
        
        Args:
            enabled: Whether the component should be enabled
        """
        self.config["enabled"] = enabled
    
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
    def deserialize(cls, data: Dict[str, Any]) -> 'BaseComponent':
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