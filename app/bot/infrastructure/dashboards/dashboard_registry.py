# app/bot/infrastructure/dashboards/dashboard_registry.py
from typing import Dict, Any, Optional, Type
import nextcord
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()


from app.bot.interfaces.dashboards.controller.dashboard_controller import DashboardController
from app.bot.interfaces.dashboards.components.base_component import BaseComponent
from app.bot.infrastructure.config.registries.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.service_factory import ServiceFactory
from nextcord.ext import tasks

class DashboardRegistry:
    """Registry for managing active dashboard controller instances."""
    
    def __init__(self, bot):
        self.bot = bot
        # --- ADD DEBUG LOG ---
        bot_id = getattr(bot.user, 'id', 'N/A')
        has_factory = hasattr(bot, 'service_factory')
        factory_type = type(getattr(bot, 'service_factory', None)).__name__
        logger.info(f"[DEBUG registry.__init__] Received bot. Bot ID: {bot_id}, Has service_factory: {has_factory}, Factory Type: {factory_type}")
        # ---------------------
        self.active_dashboards: Dict[int, DashboardController] = {}  # channel_id -> dashboard controller
        self.dashboard_types: Dict[str, Type[DashboardController]] = {}  # Maps type string to controller class (adjust if needed)
        self.component_registry = None  # Will be fetched
        self.initialized = False
        self.logger = logger
        self._refresh_active_dashboards_loop.start()
        
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

        logger.debug(f"[Activate/Update AD_ID:{active_dashboard_id} Ch:{channel_id}] Ensuring controller is active for type '{dashboard_type}'.")
        # --- ADD DEBUG LOG ---
        bot_id = getattr(self.bot.user, 'id', 'N/A')
        has_factory = hasattr(self.bot, 'service_factory')
        factory_type = type(getattr(self.bot, 'service_factory', None)).__name__
        logger.info(f"[DEBUG registry.activate] Using self.bot. Bot ID: {bot_id}, Has service_factory: {has_factory}, Factory Type: {factory_type}")
        # ---------------------

        # Check if channel exists on Discord
        channel = self.bot.get_channel(channel_id)
        if not channel or not isinstance(channel, nextcord.TextChannel):
            self.logger.warning(f"[Activate/Update AD_ID:{active_dashboard_id} Ch:{channel_id}] Channel {channel_id} not found or is not a text channel.")
            # TODO: Optionally deactivate the ActiveDashboardEntity in DB if channel deleted?
            return False

        guild_id = channel.guild.id # Get guild_id from the channel object

        # Check if controller already exists in registry
        existing_controller: Optional[DashboardController] = self.active_dashboards.get(channel_id)

        if existing_controller:
            logger.debug(f"[Activate/Update AD_ID:{active_dashboard_id} Ch:{channel_id}] Controller already exists. Updating...")
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
                logger.info(f"[Activate/Update AD_ID:{active_dashboard_id} Ch:{channel_id}] Successfully updated and redisplayed dashboard.")
                return True
            except Exception as e:
                logger.error(f"[Activate/Update AD_ID:{active_dashboard_id} Ch:{channel_id}] Error updating existing controller: {e}", exc_info=True)
                # TODO: Potentially set error state in ActiveDashboardEntity?
                return False
        else:
            logger.debug(f"[Activate/Update AD_ID:{active_dashboard_id} Ch:{channel_id}] No existing controller. Activating new one...")
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
                init_success = await controller.initialize(bot=self.bot)
                if not init_success:
                     logger.error(f"[Activate/Update AD_ID:{active_dashboard_id} Ch:{channel_id}] Failed to initialize new controller.")
                     # Decide if we should still register it? Probably not.
                     return False

                # Display dashboard (initial display)
                # display_dashboard should now return the discord.Message object or None
                msg_object = await controller.display_dashboard()
                if not msg_object:
                    logger.error(f"[Activate/Update AD_ID:{active_dashboard_id} Ch:{channel_id}] Failed to display new dashboard (display_dashboard returned None).")
                    # Decide if we should still register it? Probably not.
                    return False
                else:
                    # Update the controller's message_id with the actual ID from the newly created message
                    controller.message_id = str(msg_object.id)
                    logger.debug(f"[Activate/Update AD_ID:{active_dashboard_id} Ch:{channel_id}] Dashboard displayed successfully. Message ID: {controller.message_id}")

                # Register in active dashboards
                self.active_dashboards[channel_id] = controller
                logger.info(f"[Activate/Update AD_ID:{active_dashboard_id} Ch:{channel_id}] Activated '{dashboard_type}' dashboard.")
                return True

            except Exception as e:
                 logger.error(f"[Activate/Update AD_ID:{active_dashboard_id} Ch:{channel_id}] Error activating new dashboard controller: {e}", exc_info=True)
                 # TODO: Potentially create ActiveDashboardEntity with error state?
                 return False

    async def get_dashboard_by_type(self, dashboard_type: str) -> Optional[DashboardController]:
        """Get first dashboard controller of given type."""
        for controller in self.active_dashboards.values():
            if controller.dashboard_type == dashboard_type:
                return controller
        return None

    # --- Background Refresh Task ---
    @tasks.loop(seconds=60) # Refresh every 60 seconds
    async def _refresh_active_dashboards_loop(self):
        """Periodically refresh all active dashboards."""
        active_dashboard_ids = list(self.active_dashboards.keys())
        if not active_dashboard_ids:
            # logger.debug("No active dashboards in registry to refresh.")
            return
            
        logger.debug(f"Registry: Starting refresh cycle for {len(active_dashboard_ids)} active dashboards...")
        refreshed_count = 0
        failed_count = 0
        
        for channel_id, controller in list(self.active_dashboards.items()): # Use list() for safe iteration
            try:
                logger.debug(f"Registry: Refreshing dashboard in channel {channel_id} (Controller: {controller})...")
                await controller.refresh_data() # Fetch new data
                await controller.display_dashboard() # Update the message
                refreshed_count += 1
                logger.debug(f"Registry: Successfully refreshed dashboard in channel {channel_id}.")
            except Exception as e:
                failed_count += 1
                logger.error(f"Registry: Error refreshing dashboard in channel {channel_id} during loop: {e}", exc_info=True)
                # Optionally, consider deactivating the controller here if it fails repeatedly
                
        if refreshed_count > 0 or failed_count > 0:
            logger.debug(f"Registry: Finished refresh cycle. Refreshed: {refreshed_count}, Failed: {failed_count}/{len(active_dashboard_ids)}")
            
    @_refresh_active_dashboards_loop.before_loop
    async def before_refresh_loop(self):
        """Wait until the bot is ready before starting the loop."""
        await self.bot.wait_until_ready()
        logger.info("DashboardRegistry refresh loop is ready and starting.")