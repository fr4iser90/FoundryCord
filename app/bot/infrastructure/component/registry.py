"""
Component registry for managing UI components in the HomeLab Discord Bot.
"""
import logging
from typing import Dict, Any, Optional, Type, List

logger = logging.getLogger("homelab.components")

class ComponentRegistry:
    """
    Registry for UI components used in dashboards and other UI elements.
    
    The registry maintains a collection of component types that can be
    instantiated by the component factory.
    """
    
    def __init__(self):
        """Initialize an empty component registry."""
        self._components = {}
        logger.info("Component registry initialized")
    
    def register(self, component_type: str, component_class: Type) -> None:
        """
        Register a component class with the registry.
        
        Args:
            component_type: The type identifier for the component
            component_class: The class to instantiate for this component type
        """
        self._components[component_type] = component_class
        logger.debug(f"Registered component type: {component_type}")
    
    def get(self, component_type: str) -> Optional[Type]:
        """
        Get a component class by its type.
        
        Args:
            component_type: The type identifier for the component
            
        Returns:
            The component class or None if not found
        """
        return self._components.get(component_type)
    
    def get_all_types(self) -> List[str]:
        """
        Get all registered component types.
        
        Returns:
            List of component type identifiers
        """
        return list(self._components.keys())
    
    def clear(self) -> None:
        """Clear all registered components."""
        self._components.clear()
        logger.debug("Component registry cleared")


class DataSourceRegistry:
    """
    Registry for data sources used by UI components.
    
    Data sources provide dynamic data to components for rendering.
    """
    
    def __init__(self):
        """Initialize an empty data source registry."""
        self._data_sources = {}
        logger.info("Data source registry initialized")
    
    def register(self, source_name: str, data_source: Any) -> None:
        """
        Register a data source with the registry.
        
        Args:
            source_name: The name identifier for the data source
            data_source: The data source object or function
        """
        self._data_sources[source_name] = data_source
        logger.debug(f"Registered data source: {source_name}")
    
    def get(self, source_name: str) -> Optional[Any]:
        """
        Get a data source by its name.
        
        Args:
            source_name: The name identifier for the data source
            
        Returns:
            The data source or None if not found
        """
        return self._data_sources.get(source_name)
    
    def get_all_names(self) -> List[str]:
        """
        Get all registered data source names.
        
        Returns:
            List of data source name identifiers
        """
        return list(self._data_sources.keys())
    
    def clear(self) -> None:
        """Clear all registered data sources."""
        self._data_sources.clear()
        logger.debug("Data source registry cleared") 