# app/bot/infrastructure/dashboards/dashboard_registry.py
from typing import Dict, Any, Optional
import nextcord

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

# Import the correct, unified controller
from app.bot.interfaces.dashboards.controller.dashboard_controller import DashboardController

class DashboardRegistry:
    """Registry for managing active dashboard controller instances."""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_dashboards = {}  # channel_id -> dashboard controller
        self.logger = logger
        
    async def initialize(self):
        """Initialize the dashboard registry (simple initialization)."""
        try:
            # Activation logic moved to DashboardLifecycleService
            self.active_dashboards = {}
            self.logger.info(f"Dashboard registry initialized (Activation handled externally). ")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing dashboard registry: {e}")
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
            
    async def get_dashboard(self, channel_id: int) -> Optional[DashboardController]:
        """Get dashboard controller for a channel."""
        return self.active_dashboards.get(channel_id)
        
    async def activate_or_update_dashboard(self, 
                                           channel_id: int, 
                                           dashboard_entity: Any, # Use Any temporarily, should be DashboardEntity 
                                           config_data: Dict[str, Any] # Pass parsed config data
                                           ) -> bool:
        """Ensures a dashboard controller is active for the channel, using data from DashboardEntity."""
        # TODO: Replace Any with proper DashboardEntity type hint after checking import/availability
        
        dashboard_id = dashboard_entity.id
        dashboard_type = dashboard_entity.dashboard_type
        guild_id = dashboard_entity.guild_id
        message_id = dashboard_entity.message_id
        
        log_prefix = f"[Activate/Update DB:{dashboard_id} Ch:{channel_id}]"
        logger.info(f"{log_prefix} Ensuring controller is active.")
        
        # Check if channel exists on Discord
        channel = self.bot.get_channel(channel_id)
        if not channel:
            self.logger.warning(f"{log_prefix} Channel {channel_id} not found.")
            return False

        # Check if controller already exists in registry
        existing_controller: Optional[DashboardController] = self.active_dashboards.get(channel_id)
        
        if existing_controller:
            logger.debug(f"{log_prefix} Controller already exists. Updating...")
            try:
                # Update existing controller's state
                # Minimal update: ensure message_id is current
                existing_controller.message_id = message_id 
                existing_controller.config = config_data # Update config
                # Potentially update other entity fields if needed
                existing_controller.title = dashboard_entity.title or existing_controller.title
                existing_controller.description = dashboard_entity.description or existing_controller.description
                
                # Trigger a redisplay which should use the latest config/data
                await existing_controller.display_dashboard()
                logger.info(f"{log_prefix} Successfully updated and redisplayed dashboard.")
                return True
            except Exception as e:
                logger.error(f"{log_prefix} Error updating existing controller: {e}", exc_info=True)
                return False
        else:
            logger.debug(f"{log_prefix} No existing controller. Activating new one...")
            try:
                # Create dashboard controller using data from entity
                controller = DashboardController(
                    dashboard_id=dashboard_id,
                    channel_id=channel_id,
                    dashboard_type=dashboard_type,
                    guild_id=guild_id,
                    message_id=message_id,
                    config=config_data, # Pass loaded config
                    title=dashboard_entity.title, # Pass title from entity
                    description=dashboard_entity.description # Pass description from entity
                    # Add other kwargs from entity if needed by controller __init__
                )
                
                # Initialize controller
                init_success = await controller.initialize(self.bot)
                if not init_success:
                     logger.error(f"{log_prefix} Failed to initialize new controller.")
                     return False
                
                # Display dashboard (initial display)
                msg = await controller.display_dashboard()
                if not msg:
                    logger.error(f"{log_prefix} Failed to display new dashboard.")
                    # Decide if we should still register it? Probably not.
                    return False
                    
                # Register in active dashboards
                self.active_dashboards[channel_id] = controller
                logger.info(f"{log_prefix} Activated {dashboard_type} dashboard.")
                return True
                
            except Exception as e:
                 logger.error(f"{log_prefix} Error activating new dashboard controller: {e}", exc_info=True)
                 return False

    async def get_dashboard_by_type(self, dashboard_type: str) -> Optional[DashboardController]:
        """Get first dashboard controller of given type."""
        for controller in self.active_dashboards.values():
            if controller.dashboard_type == dashboard_type:
                return controller
        return None