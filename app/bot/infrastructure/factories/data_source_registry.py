"""Factory for creating and managing dashboard data sources."""
from typing import Dict, Any, Type, Optional
import inspect
import importlib
import pkgutil
import os

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class DataSourceRegistry:
    """Factory for creating and managing dashboard data sources."""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_sources = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize the data source registry."""
        try:
            # Auto-discover data sources
            await self._discover_data_sources()
            
            self.initialized = True
            logger.info(f"Data Source Registry initialized with {len(self.data_sources)} sources")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Data Source Registry: {e}")
            return False
            
    async def _discover_data_sources(self):
        """Automatically discover and register data sources."""
        try:
            # Base data source path
            base_path = "app.bot.infrastructure.data_sources"
            base_module = importlib.import_module(base_path)
            base_dir = os.path.dirname(base_module.__file__)
            
            # Scan for data source modules
            for _, name, is_pkg in pkgutil.iter_modules([base_dir]):
                if name.startswith("_"):
                    continue
                    
                try:
                    # Import module
                    module = importlib.import_module(f"{base_path}.{name}")
                    
                    # Find data source classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (inspect.isclass(attr) and 
                            attr_name.endswith("DataSource") and 
                            hasattr(attr, "fetch_data")):
                            
                            # Register data source
                            data_source_type = name.replace("_source", "")
                            self.register_data_source(data_source_type, attr)
                            
                except Exception as e:
                    logger.error(f"Error loading data source module {name}: {e}")
            
            # Register additional data sources manually if needed
            self._register_manual_data_sources()
            
            return True
            
        except Exception as e:
            logger.error(f"Error discovering data sources: {e}")
            return False
            
    def _register_manual_data_sources(self):
        """Register data sources that can't be discovered automatically."""
        # Example: Register system metrics data source
        try:
            from app.bot.infrastructure.data_sources.system_metrics_source import SystemMetricsDataSource
            self.register_data_source("system_metrics", SystemMetricsDataSource)
        except ImportError:
            logger.warning("Could not import SystemMetricsDataSource")
            
        # Register more data sources here as needed
        
    def register_data_source(self, source_type: str, source_class) -> None:
        """Register a data source type with its implementation class."""
        self.data_sources[source_type] = source_class
        logger.debug(f"Registered data source: {source_type}")
        
    def get_data_source(self, source_type: str) -> Optional[Type]:
        """Get a data source class by type."""
        return self.data_sources.get(source_type)
        
    def create_data_source(self, source_type: str, config: Dict[str, Any] = None) -> Optional[Any]:
        """Create a data source instance."""
        source_class = self.get_data_source(source_type)
        if not source_class:
            logger.warning(f"Data source type not found: {source_type}")
            return None
            
        try:
            return source_class(self.bot, config)
        except Exception as e:
            logger.error(f"Error creating data source {source_type}: {e}")
            return None
            
    def get_all_data_sources(self) -> Dict[str, Type]:
        """Get all registered data source types."""
        return self.data_sources.copy() 