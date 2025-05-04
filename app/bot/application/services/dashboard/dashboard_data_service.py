"""Service for fetching data for dashboard instances."""
from typing import Dict, Any, List, Optional, TYPE_CHECKING
import nextcord
from datetime import datetime

from app.shared.interface.logging.api import get_bot_logger

# --- REMOVE INCORRECT IMPORT ---
# from app.bot.infrastructure.factories.data_source_registry_factory import DataSourceRegistryFactory # OLD AND DELETED

if TYPE_CHECKING:
    from app.bot.core.main import FoundryCord
    from app.bot.infrastructure.factories.service_factory import ServiceFactory
    # --- ADD CORRECT TYPE HINT ---
    from app.bot.infrastructure.factories.data_source_registry import DataSourceRegistry

logger = get_bot_logger()

class DashboardDataService:
    """Service focused on fetching data for dashboard configurations."""
    
    def __init__(self, bot: 'FoundryCord', service_factory: 'ServiceFactory'):
        self.bot = bot
        self.service_factory = service_factory
        # --- USE CORRECT TYPE HINT ---
        self.data_source_registry: Optional['DataSourceRegistry'] = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the dashboard data service by getting dependencies."""
        logger.debug("Initializing DashboardDataService...")
        try:
            # --- GET CORRECT REGISTRY FROM SERVICE FACTORY ---
            # Use the correct service name used during registration in setup_hooks.py
            registry_instance = self.service_factory.get_service('data_source_registry')

            # Check if the retrieved instance is of the expected type (optional but good practice)
            # Need to import the actual class for instanceof check
            from app.bot.infrastructure.factories.data_source_registry import DataSourceRegistry
            if isinstance(registry_instance, DataSourceRegistry):
                 self.data_source_registry = registry_instance
                 logger.debug("DataSourceRegistry retrieved successfully.")
            elif registry_instance is not None:
                 logger.error(f"Retrieved 'data_source_registry' service is not of type DataSourceRegistry (Type: {type(registry_instance).__name__}). Data fetching will fail.")
                 self.data_source_registry = None # Ensure it's None if type is wrong
            else:
                 logger.warning("DataSourceRegistry service not found in ServiceFactory. Data fetching will be limited.")
                 self.data_source_registry = None
            # --- END GET CORRECT REGISTRY ---

            # Removed old factory instantiation

            logger.info("Dashboard Data Service initialized.")
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Dashboard Data Service: {e}", exc_info=True)
            self.initialized = False
            return False
            
    # Removed build_dashboard method
            
    # Removed build_embed method
            
    # Removed add_component_to_embed method
            
    # Removed build_view method
            
    # Removed add_component_to_view method
            
    async def fetch_data(self, data_sources_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetches data from multiple sources based on the provided configuration.

        Args:
            data_sources_config: A dictionary where keys are identifiers for the fetched data
                                 and values are configurations for the data source to use.
                                 Example: {'system_info': {'type': 'system_metrics', 'params': {}},
                                          'recent_users': {'type': 'database_query', 'query_key': 'get_recent_users'}}

        Returns:
            A dictionary containing the fetched data, keyed by the identifiers from the config.
        """
        if not self.initialized or not self.data_source_registry:
            logger.error("Cannot fetch data: DashboardDataService not initialized or DataSourceRegistry unavailable.")
            # Return empty dict to prevent downstream errors trying to access keys
            return {}

        fetched_data_results = {}
        logger.debug(f"Fetching data for sources: {list(data_sources_config.keys())}")

        for data_key, source_config in data_sources_config.items():
            source_type = source_config.get('type')
            source_params = source_config.get('params', {})

            if not source_type:
                logger.warning(f"Skipping data source for key '{data_key}': Missing 'type' in configuration.")
                continue

            # --- USE CORRECT REGISTRY METHOD ---
            DataSourceClass = self.data_source_registry.get_data_source(source_type)
            if not DataSourceClass:
                logger.warning(f"Skipping data source for key '{data_key}': Type '{source_type}' not found in DataSourceRegistry.")
                continue
            # --- END USE CORRECT REGISTRY METHOD ---

            try:
                # Instantiate the data source (passing bot and params)
                # Assuming data source constructors accept (bot, params_dict)
                data_source_instance = DataSourceClass(self.bot, source_params)

                if hasattr(data_source_instance, 'fetch_data') and callable(data_source_instance.fetch_data):
                    data = await data_source_instance.fetch_data()
                    fetched_data_results[data_key] = data
                    logger.debug(f"Successfully fetched data for key '{data_key}' using source type '{source_type}'.")
                else:
                    logger.warning(f"Data source type '{source_type}' instance does not have a callable 'fetch_data' method.")

            except Exception as e:
                logger.error(f"Error fetching data for key '{data_key}' using source type '{source_type}': {e}", exc_info=True)
                fetched_data_results[data_key] = None # Indicate error for this key

        return fetched_data_results 