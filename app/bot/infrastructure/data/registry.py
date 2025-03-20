"""
Data registry for managing data sources in the HomeLab Discord Bot.
"""
import logging
from typing import Dict, Any, Optional, List, Callable

logger = logging.getLogger("homelab.components")

class DataSourceRegistry:
    """
    Registry for data sources used by UI components.
    
    Data sources provide dynamic data to components for rendering.
    """
    
    def __init__(self):
        """Initialize an empty data source registry."""
        self._data_sources = {}
        logger.info("Data source registry initialized")
    
    def register(self, source_name: str, data_source: Callable) -> None:
        """
        Register a data source with the registry.
        
        Args:
            source_name: The name identifier for the data source
            data_source: The data source function or object
        """
        self._data_sources[source_name] = data_source
        logger.debug(f"Registered data source: {source_name}")
    
    def get(self, source_name: str) -> Optional[Callable]:
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