# app/bot/application/services/dashboard/dashboard_lifecycle_service.py
from typing import Dict, Any, Optional, List # Added Optional, List
import nextcord # Add import for nextcord types
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

# Imports needed for activation logic
from app.shared.infrastructure.database.session.context import session_context
# Use the correct, new repository and entity
from app.shared.infrastructure.repositories.dashboards.active_dashboard_repository_impl import ActiveDashboardRepositoryImpl
from app.shared.infrastructure.models.dashboards import ActiveDashboardEntity # Import the correct entity
# Add import for the configuration repository
from app.shared.infrastructure.repositories.dashboards.dashboard_configuration_repository_impl import DashboardConfigurationRepositoryImpl
# Add import for the configuration entity
from app.shared.infrastructure.models.dashboards import ActiveDashboardEntity, DashboardConfigurationEntity
from datetime import datetime


class DashboardLifecycleService:
    """Manages the lifecycle of all dashboards"""
    
    def __init__(self, bot):
        self.bot = bot
        # --- ADD DEBUG LOG ---
        bot_id = getattr(bot.user, 'id', 'N/A')
        has_factory = hasattr(bot, 'service_factory')
        factory_type = type(getattr(bot, 'service_factory', None)).__name__
        logger.debug(f"[DashboardLifecycleService] Initializing. Bot ID: {bot_id}, Has service_factory: {has_factory}, Factory Type: {factory_type}")
        # ---------------------
        self.registry = None # Registry will handle the actual controllers/views
    
    async def initialize(self):
        """Initialize the lifecycle service WITHOUT activating DB dashboards yet."""
        # Import registry here to avoid circular dependencies if registry uses this service
        from app.bot.infrastructure.dashboards.dashboard_registry import DashboardRegistry
        self.registry = DashboardRegistry(self.bot)
        # Registry initialization might load component definitions, etc.
        await self.registry.initialize()

        # --- REMOVE Activation from here ---
        # await self.activate_db_configured_dashboards() 
        # --- END REMOVE ---

        logger.debug("[DashboardLifecycleService] Initialized (DB activation deferred to on_ready).")
        return True
    
    async def activate_db_configured_dashboards(self):
        """Loads active dashboards from DB and activates/updates them in the registry."""
        logger.debug("[DashboardLifecycleService] Attempting to activate dashboards configured in the database...")
        count = 0
        failed_count = 0
        activated_ids_to_update: Dict[int, Dict[str, Any]] = {} # Store IDs and new message IDs needing update

        try:
            # --- Initial Read Session ---
            async with session_context() as initial_session:
                repo = ActiveDashboardRepositoryImpl(initial_session)
                active_dashboards: List[ActiveDashboardEntity] = await repo.list_all_active()
                logger.debug(f"[DashboardLifecycleService] Found {len(active_dashboards)} active dashboard instances in the database.")

                for active_dashboard in active_dashboards:
                    try:
                        logger.debug(f"[DashboardLifecycleService] Processing activation for ActiveDashboard ID: {active_dashboard.id}, Channel: {active_dashboard.channel_id}")

                        if not active_dashboard.configuration:
                            logger.warning(f"[DashboardLifecycleService] Skipping activation for ActiveDashboard {active_dashboard.id}: Configuration relationship not loaded.")
                            failed_count += 1
                            continue

                        channel_id_str = active_dashboard.channel_id
                        dashboard_config = active_dashboard.configuration
                        config_data = dashboard_config.config or {}
                        dashboard_type = dashboard_config.dashboard_type
                        original_message_id = active_dashboard.message_id # Store original message_id

                        if not channel_id_str:
                             logger.warning(f"[DashboardLifecycleService] Skipping activation for ActiveDashboard {active_dashboard.id}: Missing channel_id.")
                             failed_count += 1
                             continue

                        # Convert channel_id to int for registry usage
                        try:
                            channel_id_int = int(channel_id_str)
                        except ValueError:
                            logger.error(f"[DashboardLifecycleService] Invalid channel_id format for ActiveDashboard {active_dashboard.id}: {channel_id_str}")
                            failed_count += 1
                            continue

                        # --- Call the registry to activate/update ---
                        success = await self.registry.activate_or_update_dashboard(
                            channel_id=channel_id_int,
                            dashboard_type=dashboard_type,
                            config_data=config_data,
                            active_dashboard_id=active_dashboard.id,
                            message_id=original_message_id # Pass original ID for initial edit attempt
                        )

                        if success:
                             count += 1
                             logger.debug(f"[DashboardLifecycleService] Registry successfully activated/updated controller for channel {channel_id_int}.")
                             # --- Check if message_id needs update AFTER successful activation ---
                             controller = await self.registry.get_dashboard(channel_id_int)
                             updated_message_id = None
                             if controller:
                                 if hasattr(controller, 'message_id') and controller.message_id:
                                     updated_message_id = str(controller.message_id)
                                 else:
                                     logger.debug(f"[DashboardLifecycleService] ActiveDashboard {active_dashboard.id}: Controller retrieved but has no message_id attribute or it's None.")

                                 # Compare and queue for update
                                 if updated_message_id and updated_message_id != original_message_id:
                                     logger.debug(f"[DashboardLifecycleService] ActiveDashboard {active_dashboard.id}: Message ID changed from '{original_message_id}' to '{updated_message_id}'. Queuing for DB update.")
                                     activated_ids_to_update[active_dashboard.id] = {
                                         'message_id': updated_message_id,
                                         'channel_id': channel_id_int
                                     }
                                 elif not updated_message_id and original_message_id:
                                     logger.warning(f"[DashboardLifecycleService] ActiveDashboard {active_dashboard.id}: Controller lost message ID '{original_message_id}' after activation. Not updating DB.")
                                 elif not updated_message_id:
                                     logger.debug(f"[DashboardLifecycleService] ActiveDashboard {active_dashboard.id}: Controller has no message ID after activation (likely first creation or fetch failed).")
                                 else: # updated_message_id == original_message_id
                                     logger.debug(f"[DashboardLifecycleService] ActiveDashboard {active_dashboard.id}: Message ID '{original_message_id}' remains correct.")
                             else:
                                 logger.error(f"[DashboardLifecycleService] Failed to retrieve controller for channel {channel_id_int} (ActiveDashboard ID: {active_dashboard.id}) after activation via get_dashboard.")
                             # --- End Message ID Update Check ---
                        else:
                             failed_count += 1
                             logger.warning(f"[DashboardLifecycleService] Registry activation/update failed for ActiveDashboard {active_dashboard.id} in channel {channel_id_str}.")

                    except Exception as activation_err:
                         failed_count += 1
                         logger.error(f"[DashboardLifecycleService] Error during activation loop for ActiveDashboard {active_dashboard.id}: {activation_err}", exc_info=True)
            # --- End Initial Read Session ---

            # --- Separate Session for Updates ---
            if activated_ids_to_update:
                logger.debug(f"[DashboardLifecycleService] Persisting {len(activated_ids_to_update)} updated message IDs to the database...")
                async with session_context() as update_session:
                    update_repo = ActiveDashboardRepositoryImpl(update_session)
                    updated_count = 0
                    update_failed_count = 0
                    for db_id, update_info in activated_ids_to_update.items():
                        new_msg_id = update_info['message_id']
                        ch_id = update_info['channel_id']
                        try:
                            persist_success = await update_repo.set_message_id(db_id, new_msg_id)
                            if persist_success:
                                logger.debug(f"[DashboardLifecycleService] Successfully persisted message_id '{new_msg_id}' for ActiveDashboard {db_id} (Channel: {ch_id}).")
                                updated_count += 1
                            else:
                                logger.warning(f"[DashboardLifecycleService] Failed to persist updated message_id for ActiveDashboard {db_id} (Channel: {ch_id}). Repo returned False.")
                                update_failed_count += 1
                        except Exception as persist_err:
                            logger.error(f"[DashboardLifecycleService] Error persisting message_id for ActiveDashboard {db_id} (Channel: {ch_id}): {persist_err}", exc_info=True)
                            update_failed_count += 1
                logger.debug(f"[DashboardLifecycleService] Finished persisting message IDs. Successful: {updated_count}, Failed: {update_failed_count}")
            else:
                 logger.debug("[DashboardLifecycleService] No message IDs needed database persistence after activation.")
            # --- End Separate Update Session ---

        except Exception as e:
            # Check for the specific UndefinedTableError vs other errors
            if isinstance(e, (ImportError, AttributeError)):
                 logger.error(f"[DashboardLifecycleService] Failed to activate DB dashboards due to code error (likely missing import/method): {e}", exc_info=True)
            elif "does not exist" in str(e).lower(): # Catch DB errors more specifically
                 logger.error(f"[DashboardLifecycleService] Failed to activate DB dashboards due to DATABASE TABLE error: {e}. Ensure migrations are run.", exc_info=False) # Don't need full trace for known DB issue
            else:
                logger.error(f"[DashboardLifecycleService] Failed to activate DB configured dashboards: {e}", exc_info=True)
            
        logger.debug(f"[DashboardLifecycleService] Finished DB dashboard activation. Activated/Updated in Registry: {count}, Failed Registry Activation: {failed_count}")

    async def sync_dashboard_from_snapshot(self, 
                                          channel: nextcord.TextChannel, 
                                          config_name: str, 
                                          dashboard_type: str, 
                                          config_data: Dict[str, Any]
                                          ) -> bool:
        """
        Processes a full dashboard configuration (passed as config_data) originating from a guild template,
        using the provided config_name and dashboard_type. Ensures the corresponding dashboard is active and up-to-date.
        """
        logger.debug(f"[DashboardLifecycleService] Received sync request for channel {channel.id}. Config Name: '{config_name}', Type: '{dashboard_type}'.")

        if not config_data or not config_name or not dashboard_type:
            logger.error(f"[DashboardLifecycleService] Received missing config_data, config_name, or dashboard_type for channel {channel.id}. Cannot sync.")
            return False

        # --- REMOVED INCORRECT PARSING BLOCK ---

        active_dashboard_entity = None
        active_dashboard_id = None
        current_message_id = None
        configuration_entity = None
        # We receive name/type as args now, use them directly later.

        try:
            async with session_context() as session:
                # Instantiate repositories within the session
                config_repo = DashboardConfigurationRepositoryImpl(session)
                active_repo = ActiveDashboardRepositoryImpl(session)

                # 1. Find the corresponding DashboardConfigurationEntity by the PASSED name
                # We still need the entity to get its ID for linking.
                configuration_entity = await config_repo.find_by_name(config_name) 
                if not configuration_entity:
                    logger.error(f"[DashboardLifecycleService] Could not find DashboardConfiguration named '{config_name}' referenced by sync request for channel {channel.id}.")
                    return False
                
                # Optional: Validate the type from DB matches the passed type
                if configuration_entity.dashboard_type != dashboard_type:
                     logger.error(f"[DashboardLifecycleService] Mismatch between passed dashboard_type ('{dashboard_type}') and DB type ('{configuration_entity.dashboard_type}') for config name '{config_name}'. Aborting sync for channel {channel.id}.")
                     return False

                logger.debug(f"[DashboardLifecycleService] Found DashboardConfiguration ID: {configuration_entity.id} for name '{config_name}'. Type: '{dashboard_type}'.")
                
                # 2. Find or Create ActiveDashboardEntity for the channel_id
                active_dashboard_entity = await active_repo.get_by_channel_id(str(channel.id))
                
                # --- Find/Create/Update logic for ActiveDashboardEntity ---
                if active_dashboard_entity:
                    # Instance Exists: Check for updates
                    logger.debug(f"[DashboardLifecycleService] Found existing ActiveDashboard ID: {active_dashboard_entity.id} for channel {channel.id}.")
                    active_dashboard_id = active_dashboard_entity.id
                    current_message_id = active_dashboard_entity.message_id 

                    update_data = {}
                    if active_dashboard_entity.dashboard_configuration_id != configuration_entity.id:
                        update_data['dashboard_configuration_id'] = configuration_entity.id
                        logger.debug(f"ActiveDashboard {active_dashboard_id} needs config ID update.")
                    if not active_dashboard_entity.is_active:
                         update_data['is_active'] = True
                         logger.debug(f"ActiveDashboard {active_dashboard_id} needs reactivation.")
                    # TODO: config_override check

                    if update_data:
                        logger.debug(f"Updating ActiveDashboard {active_dashboard_id}...")
                        updated_entity = await active_repo.update(active_dashboard_id, update_data)
                        if updated_entity:
                             logger.debug(f"Successfully updated ActiveDashboard {active_dashboard_id}.")
                             active_dashboard_entity = updated_entity
                        else:
                             logger.error(f"Failed to update ActiveDashboard {active_dashboard_id}.")
                             # Continue anyway?
                    else:
                        logger.debug(f"ActiveDashboard {active_dashboard_id} is already up-to-date.")
                else:
                    # Instance Does Not Exist: Create it
                    logger.debug(f"No existing ActiveDashboard for channel {channel.id}. Creating new one linked to config '{config_name}' (ID: {configuration_entity.id}).")
                    create_data = {
                        'guild_id': str(channel.guild.id),
                        'channel_id': str(channel.id),
                        'dashboard_configuration_id': configuration_entity.id,
                        'message_id': None,
                        'is_active': True
                    }
                    created_entity = await active_repo.create(**create_data)
                    if created_entity:
                        logger.debug(f"Successfully created ActiveDashboard ID: {created_entity.id}.")
                        active_dashboard_entity = created_entity
                        active_dashboard_id = created_entity.id
                    else:
                        logger.error(f"Failed to create new ActiveDashboard for channel {channel.id} linked to config '{config_name}'.")
                        return False
                # --- End Find/Create/Update ---

            # --- Session ends, commit ---

        except Exception as e:
            logger.error(f"[DashboardLifecycleService] Database error during sync for channel {channel.id}: {e}", exc_info=True)
            return False 

        # --- Activation/Update in Registry ---
        if not active_dashboard_entity: 
             logger.error(f"Logic error: active_dashboard_entity is None after DB operations for channel {channel.id}.")
             return False
             
        logger.debug(f"Proceeding to activate/update registry for channel {channel.id} (ActiveDB ID: {active_dashboard_id}). Type: {dashboard_type}")
        try:
            # Use the PASSED dashboard_type and config_data
            registry_success = await self.registry.activate_or_update_dashboard(
                channel_id=channel.id,
                dashboard_type=dashboard_type, # Use PASSED type
                config_data=config_data,       # Use PASSED data dict
                active_dashboard_id=active_dashboard_id, 
                message_id=current_message_id 
            )
            
            if not registry_success:
                logger.error(f"Registry activation/update failed for channel {channel.id} (ActiveDB ID: {active_dashboard_id}).")
                return False 
                
            # --- Message ID Update Logic (remains the same) ---
            controller = await self.registry.get_dashboard(channel.id)
            new_message_id = None
            if controller and hasattr(controller, 'message_id') and controller.message_id:
                 new_message_id = str(controller.message_id)
                 
            if new_message_id and new_message_id != current_message_id:
                logger.info(f"Message ID for channel {channel.id} changed: '{current_message_id}' -> '{new_message_id}'. Persisting...")
                async with session_context() as update_session:
                     update_repo = ActiveDashboardRepositoryImpl(update_session)
                     persist_success = await update_repo.set_message_id(active_dashboard_id, new_message_id)
                     if persist_success:
                          logger.debug(f"Successfully persisted message_id {new_message_id}.")
                     else:
                          logger.warning(f"Failed to persist message_id {new_message_id} for ActiveDashboard {active_dashboard_id}.")
            # ... (rest of message_id logging)
            
            logger.info(f"[DashboardLifecycleService] Successfully synced dashboard from snapshot for channel {channel.id}.")
            return True
            
        except Exception as e:
            logger.error(f"[DashboardLifecycleService] Error during registry activation for channel {channel.id} (ActiveDB ID: {active_dashboard_id}): {e}", exc_info=True)
            return False
    
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
            logger.error(f"Could not refresh dashboard for channel {channel_id}: Controller invalid or missing display_dashboard method.")
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