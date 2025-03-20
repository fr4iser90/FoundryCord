"""
Component factory for creating UI components in the HomeLab Discord Bot.
"""
import logging
from typing import Dict, Any, Optional

from app.bot.infrastructure.component.registry import ComponentRegistry

logger = logging.getLogger("homelab.components")

class ComponentFactory:
    """
    Factory for creating UI components from registered component types.
    
    The factory uses the component registry to instantiate components
    based on their type and configuration.
    """
    
    def __init__(self, registry: ComponentRegistry):
        """
        Initialize the component factory with a registry.
        
        Args:
            registry: The component registry to use for component creation
        """
        self.registry = registry
        logger.info("Component factory initialized with registry")
    
    def create(self, component_type: str, config: Dict[str, Any]) -> Optional[Any]:
        """
        Create a component instance from its type and configuration.
        
        Args:
            component_type: The type identifier for the component
            config: Configuration dictionary for the component
            
        Returns:
            The created component instance or None if the type is not registered
        """
        component_class = self.registry.get(component_type)
        if not component_class:
            logger.warning(f"Component type not found: {component_type}")
            return None
        
        try:
            instance = component_class(**config)
            logger.debug(f"Created component of type: {component_type}")
            return instance
        except Exception as e:
            logger.error(f"Failed to create component of type {component_type}: {str(e)}")
            return None
    
    def create_from_template(self, template: Dict[str, Any]) -> Optional[Any]:
        """
        Create a component from a template dictionary.
        
        Args:
            template: Dictionary containing 'type' and 'config' keys
            
        Returns:
            The created component instance or None if creation fails
        """
        if 'type' not in template or 'config' not in template:
            logger.error("Invalid component template: missing 'type' or 'config'")
            return None
        
        return self.create(template['type'], template['config']) 