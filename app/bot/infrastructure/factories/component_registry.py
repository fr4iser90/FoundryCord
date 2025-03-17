"""Registry for dashboard components."""
import logging
from typing import Dict, Type, Any, Optional
from dataclasses import dataclass

from app.bot.interfaces.dashboards.components.base_component import BaseComponent

logger = logging.getLogger("homelab.components")

@dataclass
class ComponentDefinition:
    """Definition of a component that can be registered"""
    component_type: str
    component_class: Type[BaseComponent]
    description: str
    default_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.default_config is None:
            self.default_config = {}

class ComponentRegistry:
    """Registry for dashboard UI components"""
    
    def __init__(self):
        self._components: Dict[str, ComponentDefinition] = {}
        logger.info("Component registry initialized")
        
    def register_component(self, 
                         component_type: str, 
                         component_class: Type[BaseComponent],
                         description: str,
                         default_config: Optional[Dict[str, Any]] = None) -> None:
        """Register a component type with the registry"""
        if component_type in self._components:
            logger.warning(f"Component type '{component_type}' already registered, overwriting")
            
        self._components[component_type] = ComponentDefinition(
            component_type=component_type,
            component_class=component_class,
            description=description,
            default_config=default_config or {}
        )
        logger.info(f"Registered component type: {component_type}")
    
    def get_component_definition(self, component_type: str) -> Optional[ComponentDefinition]:
        """Get a component definition by type"""
        if component_type not in self._components:
            logger.warning(f"Component type '{component_type}' not found in registry")
            return None
        return self._components[component_type]
    
    def get_all_component_types(self) -> list[str]:
        """Get all registered component types"""
        return list(self._components.keys())
    
    def has_component(self, component_type: str) -> bool:
        """Check if a component type is registered"""
        return component_type in self._components 