"""Registry for dashboard components."""
from typing import Dict, Any, Type, Optional
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class ComponentRegistry:
    """Registry for dashboard component types."""
    
    def __init__(self):
        self.components = {}
        
    def register_component(self, component_type: str, component_class):
        """Register a component type with its implementation class."""
        self.components[component_type] = component_class
        logger.debug(f"Registered component: {component_type}")
        
    def get_component(self, component_type: str):
        """Get component implementation class for a type."""
        return self.components.get(component_type)
        
    def get_all_components(self):
        """Get all registered component types."""
        return self.components 