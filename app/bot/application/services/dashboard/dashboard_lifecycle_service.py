# app/bot/application/services/dashboard/dashboard_lifecycle_service.py
from typing import Dict, Any, Optional # Added Optional
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

# Imports needed for activation logic
from app.shared.infrastructure.database.session.context import session_context
from app.shared.infrastructure.repositories.discord.dashboard_repository_impl import DashboardRepositoryImpl
from app.shared.infrastructure.models.dashboards.dashboard_entity import DashboardEntity # Import the entity

class DashboardLifecycleService:
    """Manages the lifecycle of all dashboards"""
    
    def __init__(self, bot):
        self.bot = bot
        self.registry = None
    
    async def initialize(self):
        """Initialize all dashboards"""
        from app.bot.infrastructure.dashboards.dashboard_registry import DashboardRegistry
        self.registry = DashboardRegistry(self.bot)
        await self.registry.initialize()
        
        # Activate dashboards based on database configuration
        # TODO: [REFACTORING] Implement dashboard activation based on loading active 
        #       DashboardEntity records from the database for relevant guilds/channels.
        #       This replaces the old logic based on static constants.
        # logger.warning("Dashboard activation logic needs rework based on DB entities.")
        # Example call (implementation TBD):
        await self.activate_db_configured_dashboards()
        
        return True
    
    async def activate_db_configured_dashboards(self):
        """Loads active dashboards from DB and activates/updates them in the registry."""
        logger.info("Attempting to activate dashboards configured in the database...")
        count = 0
        failed_count = 0
        try:
            async with session_context() as session:
                repo = DashboardRepositoryImpl(session)
                active_dashboards: List[DashboardEntity] = await repo.get_active_dashboards()
                logger.info(f"Found {len(active_dashboards)} active dashboard configurations in the database.")
                
                for dashboard_entity in active_dashboards:
                    try:
                        logger.debug(f"Processing activation for Dashboard DB ID: {dashboard_entity.id}, Channel: {dashboard_entity.channel_id}")
                        # Ensure required fields are present
                        if not all([dashboard_entity.id, dashboard_entity.channel_id, dashboard_entity.dashboard_type]):
                             logger.warning(f"Skipping activation for dashboard entity {dashboard_entity.id} due to missing required fields (channel_id, dashboard_type).")
                             failed_count += 1
                             continue
                             
                        # Config data is stored directly on the entity
                        config_data = dashboard_entity.config or {}
                             
                        # Call the registry to handle activation/update
                        success = await self.registry.activate_or_update_dashboard(
                            channel_id=int(dashboard_entity.channel_id), # Ensure channel_id is int
                            dashboard_entity=dashboard_entity, # Pass the whole entity
                            config_data=config_data # Pass the config dict
                        )
                        if success:
                             count += 1
                        else:
                             failed_count += 1
                             logger.warning(f"Activation/update failed for dashboard {dashboard_entity.id} in channel {dashboard_entity.channel_id}.")
                             
                    except Exception as activation_err:
                         failed_count += 1
                         logger.error(f"Error during activation loop for dashboard {dashboard_entity.id}: {activation_err}", exc_info=True)

        except Exception as e:
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