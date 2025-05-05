"""Service for fetching data for dashboard instances."""
from typing import Dict, Any, List, Optional, TYPE_CHECKING
import nextcord
from datetime import datetime

# Added imports for data fetching logic
import platform
import psutil
from datetime import datetime, timedelta

from app.shared.interfaces.logging.api import get_bot_logger
from app.shared.infrastructure.database.session import get_session
from app.shared.infrastructure.repositories.projects.project_repository_impl import ProjectRepositoryImpl

# --- REMOVE INCORRECT IMPORT ---
# from app.bot.infrastructure.factories.data_source_registry_factory import DataSourceRegistryFactory # OLD AND DELETED

if TYPE_CHECKING:
    from app.bot.core.main import FoundryCord
    from app.bot.infrastructure.factories.service_factory import ServiceFactory


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

            logger.debug("Dashboard Data Service initialized (DataSourceRegistry logic removed).")
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
            
    async def fetch_data(self, data_sources_config: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetches data from multiple sources based on the provided configuration.
        
        Args:
            data_sources_config: Dictionary defining the data sources.
            context: Optional dictionary containing context like guild_id.
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
                logger.debug(f"Fetching data for '{data_key}' using repository '{repo_name}' method '{method_name}'...")
                
                if not repo_name or not method_name:
                    logger.error(f"DB Repository source for '{data_key}' missing 'repository' or 'method' config.")
                    result_data[data_key] = {"error": "Missing repository or method config"}
                    continue
                    
                try:
                    guild_id = context.get('guild_id') if context else None
                    if not guild_id:
                         logger.error(f"DB Repository source for '{data_key}' requires 'guild_id' in context, but none was provided.")
                         result_data[data_key] = {"error": "guild_id missing from context"}
                         continue

                    # --- MODIFICATION START: Use get_session() and instantiate repo --- 
                    # Check if it's the project repository (for now, special case)
                    if repo_name == 'ProjectRepository':
                        async for session in get_session(): # Get session via context manager
                            repository_instance = ProjectRepositoryImpl(session)
                            repository_method = getattr(repository_instance, method_name, None)
                            
                            if not callable(repository_method):
                                logger.error(f"Method '{method_name}' not found or not callable on repository '{repo_name}' for '{data_key}'.")
                                result_data[data_key] = {"error": f"Method '{method_name}' not found on {repo_name}"}
                                # Break inner loop/session context if method invalid?
                                # For now, just log and the outer loop continues
                            else:
                                logger.debug(f"Calling {repo_name}.{method_name}(guild_id={guild_id})...")
                                fetched_repo_data = await repository_method(guild_id=guild_id)
                                # --- MODIFICATION START: Wrap list in dict ---
                                if isinstance(fetched_repo_data, list):
                                    result_data[data_key] = {"items": fetched_repo_data}
                                    logger.debug(f"Successfully fetched list data using {repo_name}.{method_name} for '{data_key}'. Wrapped in dict.")
                                else:
                                    # Assume it's already dict-like or scalar, pass as-is (or handle specific non-list types if needed)
                                    result_data[data_key] = fetched_repo_data
                                    logger.debug(f"Successfully fetched non-list data using {repo_name}.{method_name} for '{data_key}'. Type: {type(fetched_repo_data).__name__}")
                                # --- MODIFICATION END ---
                        # Exit loop after session is used
                    else:
                         # Fallback/Error for other repositories until ServiceFactory handles them
                         logger.error(f"Repository type '{repo_name}' not explicitly handled yet. ServiceFactory needs update.")
                         result_data[data_key] = {"error": f"Repository type '{repo_name}' not supported yet"}
                         continue
                    # --- MODIFICATION END ---

                except Exception as e:
                    logger.error(f"Error fetching data from DB Repository for '{data_key}' ({repo_name}.{method_name}): {e}", exc_info=True)
                    result_data[data_key] = {"error": str(e)}
                
            # --- Handle other source types (Example: Service Collector) --- 
            elif source_type == 'service_collector':
                logger.debug(f"Fetching data for '{data_key}' using service_collector...")
                # --- START IMPLEMENTATION ---
                try:
                    service_collector = self.service_factory.get_service('service_collector')
                    if not service_collector:
                        logger.error("ServiceCollector service not found in ServiceFactory.")
                        result_data[data_key] = {"error": "ServiceCollector not available"}
                        continue

                    # --- Call the specific method for game services --- 
                    # Check if the config specifies a method, default to collect_game_services
                    method_name = source_config.get('method', 'collect_game_services')
                    if method_name == 'collect_game_services':
                         logger.debug(f"Calling ServiceCollector.collect_game_services() for '{data_key}'...")
                         # Returns Dict[str, Any] e.g., {'Minecraft': 'Online', 'Factorio': 'Offline'}
                         collected_services = await service_collector.collect_game_services()
                         # Wrap the dictionary in another dict under a predictable key for template consistency
                         result_data[data_key] = {"services": collected_services} 
                         logger.debug(f"Successfully processed service_collector (game services) data for '{data_key}'.")
                    elif method_name == 'collect_all': # Or handle collect_service_metrics?
                         # Handle the metric list similar to system_collector if needed
                         logger.warning(f"Service collector configured to use '{method_name}', returning raw metrics list for '{data_key}' - processing TBD.")
                         collected_metrics = await service_collector.collect_all()
                         # Decide how to process/structure this metric list for the dashboard
                         # For now, just pass the raw list wrapped
                         result_data[data_key] = {"metrics": collected_metrics} 
                    else:
                         logger.error(f"Unsupported method '{method_name}' specified for service_collector source '{data_key}'.")
                         result_data[data_key] = {"error": f"Unsupported method: {method_name}"}
                         continue
                         
                except Exception as e:
                    logger.error(f"Error fetching data from ServiceCollector for '{data_key}': {e}", exc_info=True)
                    result_data[data_key] = {"error": str(e)}
                # --- END IMPLEMENTATION ---

            else:
                logger.warning(f"Unsupported data source type '{source_type}' for key '{data_key}'.")
                result_data[data_key] = {"error": f"Unsupported type: {source_type}"}

        logger.debug(f"DashboardDataService: Finished data fetch. Result keys: {list(result_data.keys())}")
        return result_data 