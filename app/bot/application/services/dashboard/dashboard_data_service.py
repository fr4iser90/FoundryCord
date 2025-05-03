"""Service for building dashboard instances."""
from typing import Dict, Any, List, Optional
import nextcord
from datetime import datetime

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class DashboardDataService:
    """Service focused on fetching data for dashboard configurations.
       (Formerly responsible for building UI elements as well).
    """
    
    def __init__(self, bot):
        self.bot = bot
        # Removed component_registry dependency
        self.data_source_registry = None
        
    async def initialize(self):
        """Initialize the dashboard data service."""
        try:
            # Get registry services
            # Removed component_registry logic
            self.data_source_registry = self.bot.get_service('data_source_registry')
            
            # Removed component_registry check
                
            if not self.data_source_registry:
                logger.warning("Data Source Registry service not available - data fetching will be limited.")
                # We'll continue without it, fetch_data has fallback
                
            logger.info("Dashboard Builder/Data Service initialized.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Dashboard Builder/Data Service: {e}")
            return False
            
    # Removed build_dashboard method
            
    # Removed build_embed method
            
    # Removed add_component_to_embed method
            
    # Removed build_view method
            
    # Removed add_component_to_view method
            
    async def fetch_data(self, data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from all data sources specified in the config."""
        data = {}
        
        # Fallback mechanism if registry isn't available
        if not self.data_source_registry:
            logger.warning("Data Source Registry not available. Attempting fallback data sources.")
            # Try to use system metrics service directly as a fallback
            try:
                system_metrics = self.bot.get_service('system_metrics')
                if system_metrics:
                    # Assuming 'system_metrics' is a conventional key if registry is missing
                    if 'system_metrics' in data_sources:
                        logger.debug("Fetching system_metrics via fallback.")
                        data['system_metrics'] = await system_metrics.get_metrics()
                    else:
                         logger.debug("System metrics service found but not requested in data_sources.")
                else:
                    logger.warning("System metrics service not found for fallback.")
            except Exception as fallback_err:
                 logger.error(f"Error during fallback data fetching: {fallback_err}")
            return data # Return whatever fallback could get
        
        # Primary mechanism using the registry
        for source_id, source_config in data_sources.items():
            try:
                source_type = source_config.get('type')
                if not source_type:
                     logger.warning(f"Data source config missing 'type' for key '{source_id}'")
                     continue
                     
                data_source = self.data_source_registry.create_data_source(source_type, source_config)
                
                if not data_source:
                    logger.warning(f"Could not create data source instance for type: {source_type}")
                    continue
                    
                # Fetch data
                logger.debug(f"Fetching data from source '{source_id}' (type: {source_type})")
                result = await data_source.fetch_data(source_config.get('params', {}))
                data[source_id] = result
                
            except Exception as e:
                logger.error(f"Error fetching data from source {source_id} (type: {source_config.get('type', 'N/A')}): {e}", exc_info=True)
                data[source_id] = {"error": str(e)} # Include error in data
                
        return data 