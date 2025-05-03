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
                                           # Accept the new parameters passed by LifecycleService
                                           dashboard_type: str,
                                           config_data: Dict[str, Any],
                                           active_dashboard_id: int, # ID of the ActiveDashboardEntity
                                           message_id: Optional[str] # Message ID from ActiveDashboardEntity
                                           ) -> bool:
        """Ensures a dashboard controller is active for the channel, using the provided configuration."""

        log_prefix = f"[Activate/Update AD_ID:{active_dashboard_id} Ch:{channel_id}]"
        logger.info(f"{log_prefix} Ensuring controller is active for type '{dashboard_type}'.")

        # Check if channel exists on Discord
        channel = self.bot.get_channel(channel_id)
        if not channel or not isinstance(channel, nextcord.TextChannel):
            self.logger.warning(f"{log_prefix} Channel {channel_id} not found or is not a text channel.")
            # TODO: Optionally deactivate the ActiveDashboardEntity in DB if channel deleted?
            return False

        guild_id = channel.guild.id # Get guild_id from the channel object

        # Check if controller already exists in registry
        existing_controller: Optional[DashboardController] = self.active_dashboards.get(channel_id)

        if existing_controller:
            logger.debug(f"{log_prefix} Controller already exists. Updating...")
            try:
                # Update existing controller's state
                existing_controller.dashboard_id = active_dashboard_id # Update with ActiveDashboardEntity ID
                existing_controller.dashboard_type = dashboard_type
                existing_controller.message_id = message_id
                existing_controller.config = config_data # Update config
                # Get title/description from config_data or use defaults
                existing_controller.title = config_data.get('metadata', {}).get('title', dashboard_type.replace('_', ' ').title())
                existing_controller.description = config_data.get('metadata', {}).get('description', '')

                # Trigger a redisplay which should use the latest config/data
                await existing_controller.display_dashboard()
                logger.info(f"{log_prefix} Successfully updated and redisplayed dashboard.")
                return True
            except Exception as e:
                logger.error(f"{log_prefix} Error updating existing controller: {e}", exc_info=True)
                # TODO: Potentially set error state in ActiveDashboardEntity?
                return False
        else:
            logger.debug(f"{log_prefix} No existing controller. Activating new one...")
            try:
                # Create dashboard controller using the new parameters
                # Get title/description from config_data or use defaults
                title = config_data.get('metadata', {}).get('title', dashboard_type.replace('_', ' ').title())
                description = config_data.get('metadata', {}).get('description', '')

                controller = DashboardController(
                    dashboard_id=active_dashboard_id, # Use ActiveDashboardEntity ID
                    channel_id=channel_id,
                    dashboard_type=dashboard_type,
                    guild_id=guild_id,
                    message_id=message_id, # Pass initial message_id (might be None)
                    config=config_data, # Pass loaded config
                    title=title,
                    description=description,
                    bot=self.bot # Pass bot instance
                )

                # Initialize controller
                # Pass bot only if initialize expects it - check DashboardController.initialize signature
                init_success = await controller.initialize() # Removed bot if not needed by init
                if not init_success:
                     logger.error(f"{log_prefix} Failed to initialize new controller.")
                     return False

                # Display dashboard (initial display)
                # display_dashboard should now return the discord.Message object or None
                msg_object = await controller.display_dashboard()
                if not msg_object:
                    logger.error(f"{log_prefix} Failed to display new dashboard (display_dashboard returned None).")
                    # Decide if we should still register it? Probably not.
                    return False
                else:
                    # Update the controller's message_id with the actual ID from the newly created message
                    controller.message_id = str(msg_object.id)
                    logger.debug(f"{log_prefix} Dashboard displayed successfully. Message ID: {controller.message_id}")

                # Register in active dashboards
                self.active_dashboards[channel_id] = controller
                logger.info(f"{log_prefix} Activated '{dashboard_type}' dashboard.")
                return True

            except Exception as e:
                 logger.error(f"{log_prefix} Error activating new dashboard controller: {e}", exc_info=True)
                 # TODO: Potentially create ActiveDashboardEntity with error state?
                 return False

    async def get_dashboard_by_type(self, dashboard_type: str) -> Optional[DashboardController]:
        """Get first dashboard controller of given type."""
        for controller in self.active_dashboards.values():
            if controller.dashboard_type == dashboard_type:
                return controller
        return None