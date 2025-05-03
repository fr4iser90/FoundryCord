# app/bot/infrastructure/dashboards/dashboard_registry.py
from typing import Dict, Any, Optional
import nextcord

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class DashboardRegistry:
    """Registry for managing active dashboard instances."""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_dashboards = {}  # channel_id -> dashboard controller
        self.logger = logger
        
    async def initialize(self):
        """Initialize the dashboard registry."""
        try:
            # Load dashboards from database
            if hasattr(self.bot, 'service_factory'):
                dashboard_repo = self.bot.service_factory.get_service('dashboard_repository')
                if dashboard_repo:
                    dashboards = await dashboard_repo.get_all_dashboards()
                    for dashboard in dashboards:
                        if dashboard.get('auto_activate', False):
                            await self.activate_dashboard(
                                dashboard_type=dashboard.get('dashboard_type'),
                                channel_id=dashboard.get('channel_id'),
                                **dashboard
                            )
                            
            self.logger.info(f"Dashboard registry initialized with {len(self.active_dashboards)} active dashboards")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing dashboard registry: {e}")
            return False
        
    async def activate_dashboard(self, dashboard_type: str, channel_id: int, **kwargs) -> bool:
        """Activate a dashboard in a channel."""
        try:
            # Check if channel exists
            channel = self.bot.get_channel(channel_id)
            if not channel:
                self.logger.warning(f"Channel {channel_id} not found for dashboard activation")
                return False
                
            # Check if dashboard already exists for this channel
            if channel_id in self.active_dashboards:
                self.logger.info(f"Dashboard already active in channel {channel_id}")
                return True
                
            # Create dashboard controller
            from app.bot.interfaces.dashboards.controller import UniversalDashboardController
            
            dashboard_id = f"{dashboard_type}_{channel_id}"
            controller = UniversalDashboardController(
                dashboard_id=dashboard_id,
                channel_id=channel_id,
                dashboard_type=dashboard_type,
                **kwargs
            )
            
            # Initialize controller
            await controller.initialize(self.bot)
            
            # Display dashboard
            await controller.display_dashboard()
            
            # Register in active dashboards
            self.active_dashboards[channel_id] = controller
            self.logger.info(f"Activated {dashboard_type} dashboard in channel {channel_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error activating dashboard: {e}")
            return False
            
    async def deactivate_dashboard(self, dashboard_type=None, channel_id=None) -> bool:
        """Deactivate a dashboard."""
        try:
            # Get dashboards to deactivate
            to_deactivate = []
            
            if channel_id is not None:
                # Deactivate by channel ID
                if channel_id in self.active_dashboards:
                    to_deactivate.append((channel_id, self.active_dashboards[channel_id]))
                    
            elif dashboard_type is not None:
                # Deactivate all dashboards of given type
                for ch_id, controller in list(self.active_dashboards.items()):
                    if controller.dashboard_type == dashboard_type:
                        to_deactivate.append((ch_id, controller))
                        
            else:
                # Deactivate all dashboards
                to_deactivate = list(self.active_dashboards.items())
                
            # Perform deactivation
            for ch_id, controller in to_deactivate:
                # Clean up controller resources
                await controller.cleanup()
                
                # Remove from registry
                del self.active_dashboards[ch_id]
                
                self.logger.info(f"Deactivated dashboard in channel {ch_id}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error deactivating dashboard: {e}")
            return False
            
    async def get_dashboard(self, channel_id: int):
        """Get dashboard controller for a channel."""
        return self.active_dashboards.get(channel_id)
        
    async def activate_or_update_dashboard(self, channel_id: int, config_id: str, message_id: Optional[int]) -> bool:
        """Ensures a dashboard controller is active for the channel, updating it or creating it as needed."""
        logger.info(f"Activating or updating dashboard for channel {channel_id} with config {config_id}")
        
        # Check if channel exists on Discord
        channel = self.bot.get_channel(channel_id)
        if not channel:
            self.logger.warning(f"Channel {channel_id} not found for dashboard activation/update")
            return False

        # Check if controller already exists in registry
        existing_controller = self.active_dashboards.get(channel_id)
        
        if existing_controller:
            logger.debug(f"Controller already exists for channel {channel_id}. Updating...")
            try:
                # Update existing controller's state if needed
                existing_controller.config_id = config_id # Assuming DynamicDashboardController uses this
                existing_controller.message_id = message_id
                # Potentially trigger a config reload and data refresh?
                await existing_controller.load_config() # Reload config based on new config_id
                await existing_controller.refresh_data() # Refresh data sources
                await existing_controller.display_dashboard() # Update the message
                logger.info(f"Successfully updated and redisplayed dashboard for channel {channel_id}")
                return True
            except Exception as e:
                logger.error(f"Error updating existing controller for channel {channel_id}: {e}", exc_info=True)
                return False
        else:
            logger.debug(f"No existing controller for channel {channel_id}. Activating new one...")
            # If controller doesn't exist, use the standard activation logic
            # We need to pass the necessary kwargs that activate_dashboard expects, 
            # potentially loading the minimal required info from the config blob or entity?
            # For now, assume config_id and message_id are sufficient, but this might need refinement.
            # It also assumes DynamicDashboardController is always used.
            # TODO: Refine kwargs passed here based on controller needs.
            dashboard_kwargs = {
                'config_id': config_id, 
                'message_id': message_id 
                # Fetch type, name etc from config blob? 
                # config_data = await self.bot.service_factory.get_service('dashboard_repository').get_dashboard_config(config_id)
                # dashboard_type = config_data.get('dashboard_type', 'dynamic') 
                # ... add other needed kwargs
            }
            # Assuming 'dynamic' type for now
            return await self.activate_dashboard(dashboard_type='dynamic', channel_id=channel_id, **dashboard_kwargs)

    async def get_dashboard_by_type(self, dashboard_type: str):
        """Get first dashboard controller of given type."""
        for controller in self.active_dashboards.values():
            if controller.dashboard_type == dashboard_type:
                return controller
        return None