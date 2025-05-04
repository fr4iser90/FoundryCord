# app/bot/application/services/dashboard/dashboard_lifecycle_service.py
from typing import Dict, Any, Optional, List # Added Optional, List
import nextcord # Add import for nextcord types
from app.shared.interface.logging.api import get_bot_logger
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
        logger.info(f"[DEBUG lifecycle_service.__init__] Received bot. Bot ID: {bot_id}, Has service_factory: {has_factory}, Factory Type: {factory_type}")
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

        logger.info("DashboardLifecycleService initialized (DB activation deferred to on_ready).")
        return True
    
    async def activate_db_configured_dashboards(self):
        """Loads active dashboards from DB and activates/updates them in the registry."""
        logger.info("Attempting to activate dashboards configured in the database...")
        count = 0
        failed_count = 0
        activated_ids_to_update: Dict[int, Dict[str, Any]] = {} # Store IDs and new message IDs needing update

        try:
            # --- Initial Read Session ---
            async with session_context() as initial_session:
                repo = ActiveDashboardRepositoryImpl(initial_session)
                active_dashboards: List[ActiveDashboardEntity] = await repo.list_all_active()
                logger.info(f"Found {len(active_dashboards)} active dashboard instances in the database.")

                for active_dashboard in active_dashboards:
                    try:
                        logger.debug(f"Processing activation for ActiveDashboard ID: {active_dashboard.id}, Channel: {active_dashboard.channel_id}")

                        if not active_dashboard.configuration:
                            logger.warning(f"Skipping activation for ActiveDashboard {active_dashboard.id}: Configuration relationship not loaded.")
                            failed_count += 1
                            continue

                        channel_id_str = active_dashboard.channel_id
                        dashboard_config = active_dashboard.configuration
                        config_data = dashboard_config.config or {}
                        dashboard_type = dashboard_config.dashboard_type
                        original_message_id = active_dashboard.message_id # Store original message_id

                        if not channel_id_str:
                             logger.warning(f"Skipping activation for ActiveDashboard {active_dashboard.id}: Missing channel_id.")
                             failed_count += 1
                             continue

                        # Convert channel_id to int for registry usage
                        try:
                            channel_id_int = int(channel_id_str)
                        except ValueError:
                            logger.error(f"Invalid channel_id format for ActiveDashboard {active_dashboard.id}: {channel_id_str}")
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
                             logger.debug(f"Registry successfully activated/updated controller for channel {channel_id_int}.")
                             # --- Check if message_id needs update AFTER successful activation ---
                             controller = await self.registry.get_dashboard(channel_id_int)
                             updated_message_id = None
                             if controller:
                                 if hasattr(controller, 'message_id') and controller.message_id:
                                     updated_message_id = str(controller.message_id)
                                 else:
                                     logger.debug(f"ActiveDashboard {active_dashboard.id}: Controller retrieved but has no message_id attribute or it's None.")

                                 # Compare and queue for update
                                 if updated_message_id and updated_message_id != original_message_id:
                                     logger.info(f"ActiveDashboard {active_dashboard.id}: Message ID changed from '{original_message_id}' to '{updated_message_id}'. Queuing for DB update.")
                                     activated_ids_to_update[active_dashboard.id] = {
                                         'message_id': updated_message_id,
                                         'channel_id': channel_id_int
                                     }
                                 elif not updated_message_id and original_message_id:
                                     logger.warning(f"ActiveDashboard {active_dashboard.id}: Controller lost message ID '{original_message_id}' after activation. Not updating DB.")
                                 elif not updated_message_id:
                                     logger.debug(f"ActiveDashboard {active_dashboard.id}: Controller has no message ID after activation (likely first creation or fetch failed).")
                                 else: # updated_message_id == original_message_id
                                     logger.debug(f"ActiveDashboard {active_dashboard.id}: Message ID '{original_message_id}' remains correct.")
                             else:
                                 logger.error(f"Failed to retrieve controller for channel {channel_id_int} after activation via get_dashboard.")
                             # --- End Message ID Update Check ---
                        else:
                             failed_count += 1
                             logger.warning(f"Registry activation/update failed for ActiveDashboard {active_dashboard.id} in channel {channel_id_str}.")

                    except Exception as activation_err:
                         failed_count += 1
                         logger.error(f"Error during activation loop for ActiveDashboard {active_dashboard.id}: {activation_err}", exc_info=True)
            # --- End Initial Read Session ---

            # --- Separate Session for Updates ---
            if activated_ids_to_update:
                logger.info(f"Persisting {len(activated_ids_to_update)} updated message IDs to the database...")
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
                                logger.debug(f"Successfully persisted message_id '{new_msg_id}' for ActiveDashboard {db_id} (Channel: {ch_id}).")
                                updated_count += 1
                            else:
                                logger.warning(f"Failed to persist updated message_id for ActiveDashboard {db_id} (Channel: {ch_id}). Repo returned False.")
                                update_failed_count += 1
                        except Exception as persist_err:
                            logger.error(f"Error persisting message_id for ActiveDashboard {db_id} (Channel: {ch_id}): {persist_err}", exc_info=True)
                            update_failed_count += 1
                logger.info(f"Finished persisting message IDs. Successful: {updated_count}, Failed: {update_failed_count}")
            else:
                 logger.info("No message IDs needed database persistence after activation.")
            # --- End Separate Update Session ---

        except Exception as e:
            # Check for the specific UndefinedTableError vs other errors
            if isinstance(e, (ImportError, AttributeError)):
                 logger.error(f"Failed to activate DB dashboards due to code error (likely missing import/method): {e}", exc_info=True)
            elif "does not exist" in str(e).lower(): # Catch DB errors more specifically
                 logger.error(f"Failed to activate DB dashboards due to DATABASE TABLE error: {e}. Ensure migrations are run.", exc_info=False) # Don't need full trace for known DB issue
            else:
                logger.error(f"Failed to activate DB configured dashboards: {e}", exc_info=True)
            
        logger.info(f"Finished DB dashboard activation. Activated/Updated in Registry: {count}, Failed Registry Activation: {failed_count}")

    async def sync_dashboard_from_snapshot(self, channel: nextcord.TextChannel, config_json: Dict[str, Any]) -> bool:
        """
        Processes a dashboard configuration snapshot from a guild template
        and ensures the corresponding dashboard is active and up-to-date.
        The snapshot is expected to be a dictionary already parsed from JSON.
        """
        logger.info(f"LifecycleService: Received sync_dashboard_from_snapshot for channel {channel.id}.")

        if not config_json:
            logger.error(f"LifecycleService: Received empty config_json dict for channel {channel.id}. Cannot sync.")
            return False

        try:
            config_name = config_json.get('name')
            dashboard_type = config_json.get('dashboard_type')
            config_data = config_json.get('config', {})

            if not config_name or not dashboard_type:
                logger.error(f"LifecycleService: Snapshot for channel {channel.id} is missing 'name' or 'dashboard_type'. Snapshot: {config_json}")
                return False

            logger.debug(f"LifecycleService: Parsed snapshot for channel {channel.id}. Config Name: '{config_name}', Type: '{dashboard_type}'")

        except Exception as e:
            logger.error(f"LifecycleService: Unexpected error processing snapshot dict for channel {channel.id}: {e}", exc_info=True)
            return False

        active_dashboard_entity = None
        active_dashboard_id = None
        current_message_id = None
        configuration_entity = None

        try:
            async with session_context() as session:
                # Instantiate repositories within the session
                config_repo = DashboardConfigurationRepositoryImpl(session)
                active_repo = ActiveDashboardRepositoryImpl(session)

                # 2. Find the corresponding DashboardConfigurationEntity by name
                configuration_entity = await config_repo.find_by_name(config_name)
                if not configuration_entity:
                    logger.error(f"LifecycleService: Could not find DashboardConfiguration named '{config_name}' referenced by snapshot for channel {channel.id}.")
                    # Decide: Should we fail here? Or try to create one? For now, fail.
                    return False
                
                logger.debug(f"LifecycleService: Found DashboardConfiguration ID: {configuration_entity.id} for name '{config_name}'.")
                
                # 3. Find or Create ActiveDashboardEntity for the channel_id
                active_dashboard_entity = await active_repo.get_by_channel_id(str(channel.id))
                
                if active_dashboard_entity:
                    # --- Instance Exists: Check for updates ---
                    logger.debug(f"LifecycleService: Found existing ActiveDashboard ID: {active_dashboard_entity.id} for channel {channel.id}.")
                    active_dashboard_id = active_dashboard_entity.id
                    current_message_id = active_dashboard_entity.message_id # Store current message ID

                    update_data = {}
                    # Check if linked configuration changed
                    if active_dashboard_entity.dashboard_configuration_id != configuration_entity.id:
                        update_data['dashboard_configuration_id'] = configuration_entity.id
                        logger.info(f"LifecycleService: ActiveDashboard {active_dashboard_id} needs config ID update ({active_dashboard_entity.dashboard_configuration_id} -> {configuration_entity.id})")
                    
                    # Check if it needs to be reactivated (if somehow deactivated)
                    if not active_dashboard_entity.is_active:
                         update_data['is_active'] = True
                         logger.info(f"LifecycleService: ActiveDashboard {active_dashboard_id} needs reactivation.")
                         
                    # TODO: Add check for config_override changes if implemented

                    if update_data:
                        logger.info(f"LifecycleService: Updating ActiveDashboard {active_dashboard_id}...")
                        updated_entity = await active_repo.update(active_dashboard_id, update_data)
                        if not updated_entity:
                             logger.error(f"LifecycleService: Failed to update ActiveDashboard {active_dashboard_id}.")
                             # Continue? Or fail? Continue for now, registry might fix it.
                        else:
                             logger.debug(f"LifecycleService: Successfully updated ActiveDashboard {active_dashboard_id}.")
                             active_dashboard_entity = updated_entity # Use updated entity going forward
                    else:
                        logger.debug(f"LifecycleService: No DB updates needed for ActiveDashboard {active_dashboard_id}.")

                else:
                    # --- Instance Does Not Exist: Create ---
                    logger.info(f"LifecycleService: No existing ActiveDashboard found for channel {channel.id}. Creating...")
                    # Ensure correct keyword arguments are passed matching ActiveDashboardEntity columns
                    new_entity = await active_repo.create(
                        # Use the correct foreign key name defined in the entity/repository
                        dashboard_configuration_id=configuration_entity.id, 
                        guild_id=str(channel.guild.id),
                        channel_id=str(channel.id),
                        is_active=True # Activate by default when syncing from template
                        # message_id will be null initially
                    )
                    # No commit needed here if create handles it or if session manages it
                    if not new_entity:
                        logger.error(f"LifecycleService: Failed to create ActiveDashboard for channel {channel.id}.")
                        return False
                    
                    # Refresh might be needed depending on session configuration
                    # await session.refresh(new_entity) 

                    active_dashboard_entity = new_entity
                    active_dashboard_id = new_entity.id
                    current_message_id = None # It's new, no message ID yet
                    logger.info(f"LifecycleService: Created new ActiveDashboard ID: {active_dashboard_id} for channel {channel.id}.")

            # --- Outside the session block ---
            # Ensure we have the necessary IDs
            if not active_dashboard_id or not configuration_entity:
                 logger.error(f"LifecycleService: Missing active_dashboard_id or configuration_entity after DB operations for channel {channel.id}. Aborting.")
                 return False
                 
            # 4. Call the registry to activate/update the controller and display
            logger.debug(f"LifecycleService: Calling registry.activate_or_update_dashboard for channel {channel.id} (ActiveDashboard ID: {active_dashboard_id})")
            if not self.registry:
                 logger.error("LifecycleService: DashboardRegistry not initialized!")
                 return False
                 
            registry_success = await self.registry.activate_or_update_dashboard(
                channel_id=channel.id,
                dashboard_type=configuration_entity.dashboard_type, # Get type from the found config entity
                config_data=configuration_entity.config or {}, # Get config JSON from the found config entity
                active_dashboard_id=active_dashboard_id,
                message_id=current_message_id # Pass the message_id we found/know
            )

            if not registry_success:
                logger.error(f"LifecycleService: Registry failed to activate/update dashboard for channel {channel.id}.")
                # Should we return False here? If activation fails, we can't get message_id.
                return False
            else:
                logger.info(f"LifecycleService: Registry successfully activated/updated dashboard controller for channel {channel.id}.")

            # 5. Get the updated message_id from the controller (if it was created/updated)
            controller = self.registry.get_dashboard(channel.id)
            updated_message_id = None
            if controller and controller.message_id:
                updated_message_id = str(controller.message_id)

            # 6. Persist the updated message_id back to the DB if it changed
            if updated_message_id and updated_message_id != current_message_id:
                logger.info(f"LifecycleService: Persisting new/updated message_id '{updated_message_id}' for ActiveDashboard {active_dashboard_id}.")
                async with session_context() as session: # Need a new session for this update
                    active_repo = ActiveDashboardRepositoryImpl(session)
                    persist_success = await active_repo.set_message_id(active_dashboard_id, updated_message_id)
                    if not persist_success:
                        logger.warning(f"LifecycleService: Failed to persist updated message_id for ActiveDashboard {active_dashboard_id}.")
                    else:
                         logger.debug(f"LifecycleService: Successfully persisted message_id for ActiveDashboard {active_dashboard_id}.")
            elif not updated_message_id:
                 logger.warning(f"LifecycleService: Controller for channel {channel.id} has no message_id after activation. Cannot persist.")
            else: # updated_message_id == current_message_id
                 logger.debug(f"LifecycleService: Message ID '{current_message_id}' is already correct for ActiveDashboard {active_dashboard_id}.")

            return True # If we got this far, consider it successful

        except Exception as e:
            logger.error(f"LifecycleService: Unexpected error during sync_dashboard_from_snapshot for channel {channel.id}: {e}", exc_info=True)
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