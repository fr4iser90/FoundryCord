"""Registry for dashboard data sources."""
from typing import Dict, Any, Type, Optional
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class DataSourceRegistry:
    """Registry for dashboard data source types."""
    
    def __init__(self):
        self.data_sources = {}
        
    def register_data_source(self, source_type: str, source_class):
        """Register a data source type with its implementation class."""
        self.data_sources[source_type] = source_class
        logger.debug(f"Registered data source: {source_type}")
        
    def get_data_source(self, source_type: str):
        """Get data source implementation class for a type."""
        return self.data_sources.get(source_type)
        
    def get_all_data_sources(self):
        """Get all registered data source types."""
        return self.data_sources 