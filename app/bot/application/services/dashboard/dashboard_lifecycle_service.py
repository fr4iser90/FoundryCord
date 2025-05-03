# app/bot/application/services/dashboard/dashboard_lifecycle_service.py
from typing import Dict, Any, Optional, List # Added Optional, List
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

# Imports needed for activation logic
from app.shared.infrastructure.database.session.context import session_context
# Use the correct, new repository and entity
from app.shared.infrastructure.repositories.dashboards.active_dashboard_repository_impl import ActiveDashboardRepositoryImpl
from app.shared.infrastructure.models.dashboards import ActiveDashboardEntity # Import the correct entity

class DashboardLifecycleService:
    """Manages the lifecycle of all dashboards"""
    
    def __init__(self, bot):
        self.bot = bot
        self.registry = None # Registry will handle the actual controllers/views
    
    async def initialize(self):
        """Initialize the lifecycle service and activate DB-configured dashboards."""
        # Import registry here to avoid circular dependencies if registry uses this service
        from app.bot.infrastructure.dashboards.dashboard_registry import DashboardRegistry
        self.registry = DashboardRegistry(self.bot)
        # Registry initialization might load component definitions, etc.
        await self.registry.initialize()
        
        # Activate dashboards based on database configuration
        await self.activate_db_configured_dashboards()
        
        return True
    
    async def activate_db_configured_dashboards(self):
        """Loads active dashboards from DB and activates/updates them in the registry."""
        logger.info("Attempting to activate dashboards configured in the database...")
        count = 0
        failed_count = 0
        try:
            async with session_context() as session:
                # Use the new repository
                repo = ActiveDashboardRepositoryImpl(session)
                # Call the method that loads active dashboards with their configurations
                active_dashboards: List[ActiveDashboardEntity] = await repo.list_all_active()
                logger.info(f"Found {len(active_dashboards)} active dashboard instances in the database.")
                
                # Iterate through the correct entities
                for active_dashboard in active_dashboards:
                    try:
                        logger.debug(f"Processing activation for ActiveDashboard ID: {active_dashboard.id}, Channel: {active_dashboard.channel_id}")
                        
                        # Check if configuration was loaded correctly
                        if not active_dashboard.configuration:
                            logger.warning(f"Skipping activation for ActiveDashboard {active_dashboard.id}: Configuration relationship not loaded.")
                            failed_count += 1
                            continue
                            
                        # --- Get required data from entities --- 
                        channel_id_str = active_dashboard.channel_id
                        dashboard_config = active_dashboard.configuration # The related DashboardConfigurationEntity
                        config_data = dashboard_config.config or {} # The JSON config from the configuration
                        dashboard_type = dashboard_config.dashboard_type # Type from configuration
                        # TODO: Implement logic for config_override from active_dashboard if needed
                        # if active_dashboard.config_override:
                        #     config_data = merge_configs(config_data, active_dashboard.config_override)

                        # Ensure channel_id is valid
                        if not channel_id_str:
                             logger.warning(f"Skipping activation for ActiveDashboard {active_dashboard.id}: Missing channel_id.")
                             failed_count += 1
                             continue
                             
                        # --- Call the registry to handle activation/update --- 
                        # The registry needs channel_id and the config JSON (from the configuration entity)
                        # It might also need the active_dashboard.id or message_id later.
                        # Adapt the signature of activate_or_update_dashboard if necessary.
                        success = await self.registry.activate_or_update_dashboard(
                            channel_id=int(channel_id_str), # Pass channel ID
                            dashboard_type=dashboard_type, # Pass the type from config
                            config_data=config_data, # Pass the config JSON from config
                            active_dashboard_id=active_dashboard.id, # Pass the ID of the active instance
                            message_id=active_dashboard.message_id # Pass the current message ID
                        )
                        if success:
                             count += 1
                        else:
                             failed_count += 1
                             logger.warning(f"Activation/update failed for ActiveDashboard {active_dashboard.id} in channel {channel_id_str}.")
                             
                    except Exception as activation_err:
                         failed_count += 1
                         logger.error(f"Error during activation loop for ActiveDashboard {active_dashboard.id}: {activation_err}", exc_info=True)

        except Exception as e:
            # Check for the specific UndefinedTableError vs other errors
            if isinstance(e, (ImportError, AttributeError)):
                 logger.error(f"Failed to activate DB dashboards due to code error (likely missing import/method): {e}", exc_info=True)
            elif "does not exist" in str(e).lower(): # Catch DB errors more specifically
                 logger.error(f"Failed to activate DB dashboards due to DATABASE TABLE error: {e}. Ensure migrations are run.", exc_info=False) # Don't need full trace for known DB issue
            else:
                logger.error(f"Failed to activate DB configured dashboards: {e}", exc_info=True)
            
        logger.info(f"Finished DB dashboard activation. Activated/Updated: {count}, Failed: {failed_count}")

    async def deactivate_dashboard(self, dashboard_type=None, channel_id=None):
        """
        Deactivate dashboard by type or channel ID
        
        Args:
            dashboard_type (str, optional): Type of dashboard to deactivate
            channel_id (int, optional): Channel ID containing the dashboard
            
        Returns:
            bool: True if dashboard was deactivated, False otherwise
        """
        if not self.registry:
            return False
            
        return await self.registry.deactivate_dashboard(dashboard_type, channel_id)
    
    async def get_active_dashboards(self):
        """
        Get list of all active dashboards
        
        Returns:
            dict: Dictionary of active dashboard controllers keyed by channel_id
        """
        if not self.registry:
            return {}
            
        return self.registry.active_dashboards
    
    async def refresh_dashboard(self, channel_id: int):
        """
        Force refresh of a dashboard
        
        Args:
            channel_id (int): Channel ID containing the dashboard
            
        Returns:
            bool: True if dashboard was refreshed, False otherwise
        """
        if not self.registry or channel_id not in self.registry.active_dashboards:
            return False
            
        dashboard_controller = self.registry.active_dashboards[channel_id]
        if dashboard_controller and hasattr(dashboard_controller, 'display_dashboard'):
             await dashboard_controller.display_dashboard()
             return True
        else:
            logger.warning(f"Could not refresh dashboard for channel {channel_id}: Controller invalid or missing display_dashboard method.")
            return False
    
    async def shutdown(self):
        """
        Perform clean shutdown of all dashboards
        
        Returns:
            bool: True if successful
        """
        if not self.registry:
            return True
            
        # Deactivate all dashboards
        for channel_id in list(self.registry.active_dashboards.keys()):
            await self.registry.deactivate_dashboard(channel_id=channel_id)
            
        return True