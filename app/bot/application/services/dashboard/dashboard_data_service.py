"""Service for fetching data for dashboard instances."""
from typing import Dict, Any, List, Optional, TYPE_CHECKING
import nextcord
from datetime import datetime

# Added imports for data fetching logic
import platform
import psutil
from datetime import datetime, timedelta

from app.shared.interface.logging.api import get_bot_logger

# --- REMOVE INCORRECT IMPORT ---
# from app.bot.infrastructure.factories.data_source_registry_factory import DataSourceRegistryFactory # OLD AND DELETED

if TYPE_CHECKING:
    from app.bot.core.main import FoundryCord
    from app.bot.infrastructure.factories.service_factory import ServiceFactory
    # --- Remove obsolete type hint --- 
    # from app.bot.infrastructure.factories.data_source_registry import DataSourceRegistry

logger = get_bot_logger()

class DashboardDataService:
    """Service focused on fetching data for dashboard configurations."""
    
    def __init__(self, bot: 'FoundryCord', service_factory: 'ServiceFactory'):
        self.bot = bot
        self.service_factory = service_factory
        # --- Remove obsolete attribute --- 
        # self.data_source_registry: Optional['DataSourceRegistry'] = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the dashboard data service by getting dependencies."""
        logger.debug("Initializing DashboardDataService...")
        try:
            # --- Remove attempt to get/check DataSourceRegistry --- 
            # registry_instance = self.service_factory.get_service('data_source_registry')
            # from app.bot.infrastructure.factories.data_source_registry import DataSourceRegistry # Removed this import
            # if isinstance(registry_instance, DataSourceRegistry):
            #      self.data_source_registry = registry_instance
            #      logger.debug("DataSourceRegistry retrieved successfully.")
            # elif registry_instance is not None:
            #      logger.error(f"Retrieved 'data_source_registry' service is not of type DataSourceRegistry (Type: {type(registry_instance).__name__}). Data fetching will fail.")
            #      self.data_source_registry = None
            # else:
            #      logger.warning("DataSourceRegistry service not found in ServiceFactory. Data fetching will be limited.")
            #      self.data_source_registry = None
            # --- END REMOVAL ---

            logger.info("Dashboard Data Service initialized (DataSourceRegistry logic removed).")
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
        """
        if not self.initialized:
            logger.error("Cannot fetch data: DashboardDataService not initialized.")
            return None # Indicate critical failure
            
        result_data: Dict[str, Any] = {}
        logger.debug(f"DashboardDataService: Starting data fetch for config: {data_sources_config}")

        for data_key, source_config in data_sources_config.items():
            source_type = source_config.get('type')
            if not source_type:
                logger.warning(f"Skipping data source '{data_key}': Missing 'type' config.")
                continue

            # --- Handle System Collector --- 
            if source_type == 'system_collector':
                logger.debug(f"Fetching data for '{data_key}' using system_collector...")
                try:
                    system_collector = self.service_factory.get_service('system_collector')
                    if not system_collector:
                        logger.error("SystemCollector service not found in ServiceFactory.")
                        result_data[data_key] = {"error": "SystemCollector not available"}
                        continue
                    
                    # Collect metrics (List[MetricModel])
                    collected_metrics = await system_collector.collect_all()
                    
                    # Transform into flat dictionary for templates
                    system_data = {}
                    for metric in collected_metrics:
                        if metric.name == "cpu_usage":
                            system_data['cpu_percent'] = round(metric.value, 1) if metric.value is not None else 'N/A'
                        elif metric.name == "memory_percent":
                            system_data['memory_percent'] = round(metric.value, 1) if metric.value is not None else 'N/A'
                        elif metric.name == "disk_percent":
                            system_data['disk_percent'] = round(metric.value, 1) if metric.value is not None else 'N/A'
                        elif metric.name == "hostname" and metric.metric_data:
                            system_data['hostname'] = metric.metric_data.get('hostname', 'N/A')
                        elif metric.name == "platform" and metric.metric_data:
                            system_data['platform'] = metric.metric_data.get('platform', 'N/A')
                        elif metric.name == "uptime" and metric.metric_data:
                            system_data['uptime'] = metric.metric_data.get('uptime', 'N/A')
                        # Add mappings for other metrics if needed by templates
                        
                    result_data[data_key] = system_data
                    logger.debug(f"Successfully processed system_collector data for '{data_key}'.")

                except Exception as e:
                    logger.error(f"Error fetching data from SystemCollector for '{data_key}': {e}", exc_info=True)
                    result_data[data_key] = {"error": str(e)}
            
            # --- Handle other source types (Example: Database) --- 
            elif source_type == 'db_repository':
                repo_name = source_config.get('repository')
                method_name = source_config.get('method')
                params = source_config.get('params', {})
                logger.debug(f"Fetching data for '{data_key}' using repository '{repo_name}' method '{method_name}'...")
                # TODO: Implement logic to get repository instance (e.g., via ServiceFactory or specific context)
                #       and call the specified method with params.
                logger.warning(f"Database repository fetching not implemented yet for '{data_key}'.")
                result_data[data_key] = {"placeholder": f"Data from {repo_name}.{method_name}"}
                
            # --- Handle other source types (Example: Service Collector) --- 
            elif source_type == 'service_collector':
                logger.debug(f"Fetching data for '{data_key}' using service_collector...")
                # TODO: Implement logic similar to system_collector for ServiceCollector
                logger.warning(f"Service collector fetching not implemented yet for '{data_key}'.")
                result_data[data_key] = {"placeholder": "Data from ServiceCollector"}

            else:
                logger.warning(f"Unsupported data source type '{source_type}' for key '{data_key}'.")
                result_data[data_key] = {"error": f"Unsupported type: {source_type}"}

        logger.debug(f"DashboardDataService: Finished data fetch. Result keys: {list(result_data.keys())}")
        return result_data 