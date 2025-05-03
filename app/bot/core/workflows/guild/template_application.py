import logging
from typing import Dict, List, Optional
import nextcord
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.models.discord.entities import GuildConfigEntity
from app.shared.interface.logging.api import get_bot_logger

# Import Domain interfaces (Repositories)
from app.shared.domain.repositories.guild_templates import (
    GuildTemplateRepository,
    GuildTemplateCategoryRepository,
    GuildTemplateChannelRepository,
    GuildTemplateCategoryPermissionRepository,
    GuildTemplateChannelPermissionRepository
)
# Import Infrastructure implementations
from app.shared.infrastructure.repositories.guild_templates.guild_template_repository_impl import GuildTemplateRepositoryImpl
from app.shared.infrastructure.repositories.guild_templates.guild_template_category_repository_impl import GuildTemplateCategoryRepositoryImpl
from app.shared.infrastructure.repositories.guild_templates.guild_template_channel_repository_impl import GuildTemplateChannelRepositoryImpl
from app.shared.infrastructure.repositories.guild_templates.guild_template_category_permission_repository_impl import GuildTemplateCategoryPermissionRepositoryImpl
from app.shared.infrastructure.repositories.guild_templates.guild_template_channel_permission_repository_impl import GuildTemplateChannelPermissionRepositoryImpl
# --- NEW: Import DiscordQueryService ---
from app.bot.application.services.discord.discord_query_service import DiscordQueryService
# --- ADDED: Import DashboardService ---
from app.bot.application.services.dashboard.dashboard_service import DashboardService

logger = get_bot_logger()

async def apply_template(self, guild_id: str, config: GuildConfigEntity, session: AsyncSession) -> bool:
    """Applies the stored template structure to the Discord guild using the provided session and config."""
    logger.info(f"[apply_template] Applying template for guild {guild_id} using provided session and config.")
    discord_guild = self.bot.get_guild(int(guild_id))
    if not discord_guild:
        logger.error(f"[apply_template] Could not find Discord guild {guild_id}")
        return False

    try:
        # Instantiate repositories using the passed session
        template_repo = GuildTemplateRepositoryImpl(session)
        # guild_config_repo is not needed here as config is passed in
        cat_repo = GuildTemplateCategoryRepositoryImpl(session)
        chan_repo = GuildTemplateChannelRepositoryImpl(session)
        cat_perm_repo = GuildTemplateCategoryPermissionRepositoryImpl(session)
        chan_perm_repo = GuildTemplateChannelPermissionRepositoryImpl(session)
        discord_query_service = DiscordQueryService(self.bot)

        dashboard_service: Optional[DashboardService] = None
        if hasattr(self.bot, 'dashboard_workflow') and self.bot.dashboard_workflow:
            dashboard_service = await self.bot.dashboard_workflow.get_dashboard_service()
        
        if not dashboard_service:
             logger.error("[apply_template] CRITICAL: DashboardService could not be retrieved from DashboardWorkflow.")


        # 1. Load Template Data (using active_template_id from passed config)
        logger.debug(f"[apply_template] Using active_template_id from passed GuildConfig.")
        if not config or config.active_template_id is None:
            logger.error(f"[apply_template] CRITICAL: Passed GuildConfig has no active_template_id.")
            return False

        active_template_id = config.active_template_id
        logger.info(f"[apply_template] Applying template ID: {active_template_id}")

        template = await template_repo.get_by_id(active_template_id)
        if not template:
            logger.error(f"[apply_template] Active template ID {active_template_id} not found.")
            return False

        # Fetch template structure using repositories (already loads needed attributes)
        template_categories = await cat_repo.get_by_template_id(template.id)
        template_channels = await chan_repo.get_by_template_id(template.id)
        # Permissions will be fetched later as needed by helpers

        logger.info(f"[apply_template] Loaded active template '{template.template_name}' (ID: {template.id}) for guild {guild_id}")
        logger.debug(f"  Template contains {len(template_categories)} categories and {len(template_channels)} channels.")

        # ----------------------------------------------------------
        # 2. Get Current Discord State (using the new service)
        # ----------------------------------------------------------
        live_guild_data = await discord_query_service.get_live_guild_structure(discord_guild)
        live_categories = live_guild_data.get('categories', {}) # Dict: {discord_cat_id: cat_data_dict}
        live_channels = live_guild_data.get('channels', {})     # Dict: {discord_chan_id: chan_data_dict}

        # --- Create Lookups for easy access ---
        # Map template category name -> template category entity
        template_categories_by_name = {cat.category_name: cat for cat in template_categories}
        # Map Discord category name -> Discord category ID (using live data)
        discord_categories_by_name = {cat_data['name']: cat_id for cat_id, cat_data in live_categories.items()}

        logger.debug(f"  Found {len(live_categories)} categories currently on Discord.")

        # ----------------------------------------------------------
        # 3. Process Categories (Create/Update on Discord based on Template)
        # ----------------------------------------------------------
        created_or_found_discord_categories = {} # Map template cat ID -> created/found discord cat object
        processed_live_category_ids = set() # Track processed Discord category IDs

        # Sort template categories by position for correct creation order
        sorted_template_categories = sorted(template_categories, key=lambda c: c.position)

        for template_cat in sorted_template_categories:
            logger.debug(f"  Processing template category: '{template_cat.category_name}' (Pos: {template_cat.position})")
        
            existing_discord_cat_id = discord_categories_by_name.get(template_cat.category_name)
            existing_discord_cat_object = None
            if existing_discord_cat_id:
                    # Fetch the object using the ID from the live data lookup
                    existing_discord_cat_object = discord_guild.get_channel(existing_discord_cat_id) 

            if existing_discord_cat_object and isinstance(existing_discord_cat_object, nextcord.CategoryChannel): 
                logger.info(f"    Category '{template_cat.category_name}' already exists on Discord (ID: {existing_discord_cat_object.id}).")
                
                # --- Check for updates ---
                updates_needed = {}
                # TODO: Check/Update position? Be careful, Discord might auto-adjust. 
                # Simple check: if existing_discord_cat_object.position != template_cat.position: updates_needed['position'] = template_cat.position
                
                if updates_needed:
                    try:
                        logger.info(f"      Updating category '{existing_discord_cat_object.name}' ({existing_discord_cat_object.id}) with changes: {updates_needed}")
                        await existing_discord_cat_object.edit(**updates_needed, reason="Applying template updates")
                        logger.debug(f"        Successfully updated category.")
                    except nextcord.Forbidden:
                        logger.error(f"        PERMISSION ERROR updating category '{existing_discord_cat_object.name}'.")
                    except nextcord.HTTPException as http_err:
                        logger.error(f"        HTTP ERROR updating category '{existing_discord_cat_object.name}': {http_err}")
                    except Exception as update_err:
                        logger.error(f"        UNEXPECTED ERROR updating category '{existing_discord_cat_object.name}': {update_err}", exc_info=True)
                else:
                    logger.debug("      No attribute updates needed for existing category.")

                # Apply permissions 
                await self._apply_category_permissions(existing_discord_cat_object, template_cat.id, cat_perm_repo)
                
                # Store mapping and mark as processed
                created_or_found_discord_categories[template_cat.id] = existing_discord_cat_object
                processed_live_category_ids.add(existing_discord_cat_object.id) 

            else:
                logger.info(f"    Category '{template_cat.category_name}' does not exist or is wrong type. Creating...")
                try:
                    # Apply permissions during creation using overwrites parameter
                    creation_overwrites = await self._prepare_permission_overwrites(
                        guild_roles=discord_guild.roles, 
                        template_perms_getter=cat_perm_repo.get_by_category_template_id, 
                        template_element_id=template_cat.id,
                        log_prefix="      [Create Cat]" # Added prefix for clarity
                    )
                    
                    # Call the category check and create helper from check_structure
                    new_discord_cat = await self.check_and_create_category(
                        discord_guild=discord_guild,
                        template_cat=template_cat,
                        creation_overwrites=creation_overwrites,
                        template_name=template.template_name,
                        session=session
                    )
                    
                    if new_discord_cat:
                        logger.debug(f"      Successfully created category via helper function")
                        # Store mapping and mark as processed
                        created_or_found_discord_categories[template_cat.id] = new_discord_cat
                        processed_live_category_ids.add(new_discord_cat.id)
                    else:
                        logger.warning(f"      Failed to create category '{template_cat.category_name}' via helper function")

                except Exception as creation_err:
                    logger.error(f"      UNEXPECTED ERROR during category creation process for '{template_cat.category_name}': {creation_err}", exc_info=True)

        # ----------------------------------------------------------
        # 4. Process Channels (Create/Update/Delete)
        # ----------------------------------------------------------
        logger.info("[apply_template] Processing channels...")
        
        # --- Create Lookups ---
        # Map template channel ID -> template channel entity
        template_channels_by_id = {chan.id: chan for chan in template_channels}
        
        # Map (name, parent_template_id) -> template channel entity (for matching channels without discord_id)
        template_channels_by_name_parent = {(chan.channel_name, chan.parent_category_template_id): chan for chan in template_channels}
        
        # Map live Discord channel ID -> live channel data dict
        live_channels_by_name_parent = {(chan_data['name'], chan_data['parent_id']): chan_data for chan_id, chan_data in live_channels.items()}

        # Keep track of live channels we've matched or created to handle deletions later
        processed_live_channel_ids = set()

        # --- Iterate through Template Channels (Create/Update) ---
        # Sort by position to encourage correct ordering, although Discord might adjust
        sorted_template_channels = sorted(template_channels, key=lambda c: c.position)

        for template_chan in sorted_template_channels:
            logger.debug(f"  Processing template channel: '{template_chan.channel_name}' (Type: {template_chan.channel_type}, Pos: {template_chan.position}, DB_ID: {template_chan.id})")

            target_discord_category = None
            if template_chan.parent_category_template_id:
                # Use the map we built during category processing
                target_discord_category = created_or_found_discord_categories.get(template_chan.parent_category_template_id)
                if not target_discord_category:
                    logger.warning(f"    Parent category (Template ID: {template_chan.parent_category_template_id}) specified in template was not found or created on Discord for channel '{template_chan.channel_name}'. Will create channel without parent.")
            
            target_parent_discord_id = target_discord_category.id if target_discord_category else None

            # --- Try to find existing Discord channel ---
            existing_discord_chan_object = None
            
            # 1. Try matching by known Discord ID (if set previously - MORE RELIABLE)
            if template_chan.discord_channel_id:
                    potential_match = discord_guild.get_channel(int(template_chan.discord_channel_id))
                    # Verify it's the correct type (or handle type changes?)
                    if potential_match and str(potential_match.type) == template_chan.channel_type:
                        existing_discord_chan_object = potential_match
                        logger.debug(f"    Found potential match by DB discord_channel_id: {existing_discord_chan_object.name} ({existing_discord_chan_object.id})")
                    else:
                            logger.warning(f"    DB discord_channel_id {template_chan.discord_channel_id} for '{template_chan.channel_name}' points to a non-existent channel or channel of wrong type ({potential_match.type if potential_match else 'None'}). Ignoring ID and trying name match.")
                            # Reset the ID in DB? For now, just proceed to name matching.
                            # await chan_repo.update(template_chan, discord_channel_id=None) # Example

            # 2. If no match by ID, try matching by name and parent category
            if not existing_discord_chan_object:
                # Use the live data lookup based on name and parent *Discord* ID
                live_match_data = live_channels_by_name_parent.get((template_chan.channel_name, target_parent_discord_id))
                if live_match_data:
                    # Fetch the actual channel object using the ID from live data
                    discord_chan_id = live_match_data.get('id') # Get the ID from the dict
                    if discord_chan_id:
                        try:
                            potential_match = discord_guild.get_channel(discord_chan_id)
                            if potential_match and str(potential_match.type) == template_chan.channel_type:
                                existing_discord_chan_object = potential_match
                                logger.debug(f"    Found potential match by name and parent: {existing_discord_chan_object.name} ({existing_discord_chan_object.id})")
                                # --- Update DB discord_channel_id (since we found it by name) ---
                                if template_chan.discord_channel_id != str(existing_discord_chan_object.id):
                                    logger.info(f"      Updating DB discord_id for template channel {template_chan.id} from {template_chan.discord_channel_id} to {existing_discord_chan_object.id}")
                                    template_chan.discord_channel_id = str(existing_discord_chan_object.id)
                                    # Mark session dirty? Changes to template_chan might need commit?
                                    # Or rely on the main session commit at the end?
                                    # Session commit will handle saving this change later
                                # -------------------------------------
                            else:
                                logger.warning(f"    Name match found for '{template_chan.channel_name}' but type is wrong ({potential_match.type if potential_match else 'None'}) vs template ({template_chan.channel_type}). Treating as non-existent.")
                        except Exception as get_chan_err_name:
                            logger.error(f"    Error getting channel object by name: {get_chan_err_name}", exc_info=True)
                    else:
                            logger.error(f"    Live channel data found for name/parent match of '{template_chan.channel_name}' but is missing 'id'. Data inconsistency from query service?")

            # --- Update or Create Channel ---
            if existing_discord_chan_object:
                processed_live_channel_ids.add(existing_discord_chan_object.id)
                logger.info(f"    Channel '{template_chan.channel_name}' already exists (ID: {existing_discord_chan_object.id}). Checking for updates...")
                
                # --- Store the channel object for dashboard logic ---
                discord_channel_object_to_use = existing_discord_chan_object
                # -------------------------------------------------
                
                # --- Check for updates ---
                updates_needed = {}
                # Name: Only update if name is different (and it wasn't found by name originally)
                # Position: Often less reliable, consider skipping or only if drastically different.
                # if existing_discord_chan_object.position != template_chan.position: updates_needed['position'] = template_chan.position
                if isinstance(existing_discord_chan_object, (nextcord.TextChannel, nextcord.ForumChannel)): # Topic only applies to these
                    if getattr(existing_discord_chan_object, 'topic', None) != template_chan.topic:
                        updates_needed['topic'] = template_chan.topic 
                if isinstance(existing_discord_chan_object, (nextcord.TextChannel, nextcord.VoiceChannel, nextcord.ForumChannel, nextcord.StageChannel)): # NSFW applies to these
                    if getattr(existing_discord_chan_object, 'nsfw', False) != template_chan.is_nsfw:
                            updates_needed['nsfw'] = template_chan.is_nsfw 
                if isinstance(existing_discord_chan_object, (nextcord.TextChannel, nextcord.ForumChannel)): # Slowmode only applies to these
                    if existing_discord_chan_object.slowmode_delay != template_chan.slowmode_delay:
                        updates_needed['slowmode_delay'] = template_chan.slowmode_delay
                # Category (Parent): Check if it needs moving
                if existing_discord_chan_object.category != target_discord_category: # Compare objects directly
                        updates_needed['category'] = target_discord_category # Move category
                
                # Add other type-specific checks here (e.g., bitrate, user_limit for voice)

                if updates_needed:
                    try:
                        logger.info(f"      Updating channel '{existing_discord_chan_object.name}' ({existing_discord_chan_object.id}) with changes: {list(updates_needed.keys())}") # Log keys only for brevity
                        await existing_discord_chan_object.edit(**updates_needed, reason="Applying template updates")
                        logger.debug(f"        Successfully updated channel.")
                    except nextcord.Forbidden:
                        logger.error(f"        PERMISSION ERROR updating channel '{existing_discord_chan_object.name}'.")
                    except nextcord.HTTPException as http_err:
                        logger.error(f"        HTTP ERROR updating channel '{existing_discord_chan_object.name}': {http_err}")
                    except Exception as update_err:
                        logger.error(f"        UNEXPECTED ERROR updating channel '{existing_discord_chan_object.name}': {update_err}", exc_info=True)
                else:
                        logger.debug("      No attribute updates needed.")

                # Always apply permissions (overwrite mode)
                await self._apply_channel_permissions(discord_channel_object_to_use, template_chan.id, chan_perm_repo)

            else:
                # --- Create Channel using Helper ---
                logger.info(f"    Channel '{template_chan.channel_name}' not found by template ID or name+parent match. Attempting check & create...")
                
                # Prepare overwrites BEFORE creation check
                creation_overwrites = await self._prepare_permission_overwrites(
                    guild_roles=discord_guild.roles, 
                    template_perms_getter=chan_perm_repo.get_by_channel_template_id, 
                    template_element_id=template_chan.id,
                    log_prefix="      [Check&Create Chan]" # Updated log prefix
                )

                # Call the channel check and create helper from check_structure
                new_discord_chan = await self.check_and_create_channel(
                    discord_guild=discord_guild,
                    template_chan=template_chan,
                    target_discord_category=target_discord_category,
                    creation_overwrites=creation_overwrites,
                    template_name=template.template_name,
                    session=session
                )

                # If helper returned a new channel, update DB and track ID
                if new_discord_chan:
                    # --- Store the channel object for dashboard logic ---
                    discord_channel_object_to_use = new_discord_chan
                    # -------------------------------------------------
                    logger.info(f"      Successfully created channel '{new_discord_chan.name}' (ID: {new_discord_chan.id})")
                    processed_live_channel_ids.add(new_discord_chan.id) # Track newly created channel ID
                else:
                    logger.warning(f"      Failed to create channel '{template_chan.channel_name}'")
                    discord_channel_object_to_use = None # Ensure it's None if creation failed

                # --- >> ADDED: Dashboard Snapshot Logic << ---
                if discord_channel_object_to_use and isinstance(discord_channel_object_to_use, nextcord.TextChannel): # Only text channels can have dashboards?
                    if template_chan.is_dashboard_enabled and template_chan.dashboard_config_snapshot:
                        if dashboard_service:
                            logger.info(f"    Dashboard enabled for '{discord_channel_object_to_use.name}'. Syncing from snapshot...")
                            await dashboard_service.sync_dashboard_from_snapshot(
                                channel=discord_channel_object_to_use, 
                                config_json=template_chan.dashboard_config_snapshot
                            )
                        else:
                             logger.warning(f"    Dashboard enabled for '{discord_channel_object_to_use.name}' but DashboardService is unavailable. Skipping snapshot sync.")
                    elif template_chan.is_dashboard_enabled:
                         logger.warning(f"    Dashboard is enabled for '{discord_channel_object_to_use.name}' but dashboard_config_snapshot is NULL in the template. Skipping.")
                    else:
                        logger.debug(f"    Dashboard is not enabled for '{discord_channel_object_to_use.name}' in template.")
                        # Optional TODO: Add logic here to deactivate/delete dashboard if needed
                        # if dashboard_service:
                        #    await dashboard_service.deactivate_channel_dashboard(discord_channel_object_to_use.id)
                elif discord_channel_object_to_use:
                     logger.debug(f"    Skipping dashboard sync for non-text channel '{discord_channel_object_to_use.name}' (Type: {discord_channel_object_to_use.type})")
                # --- >> END Dashboard Snapshot Logic << ---

        # ----------------------------------------------------------
        # 6. Process Channels (Delete from Discord if not in Template - Optional)
        # ----------------------------------------------------------
        # Read the flag from the loaded guild configuration
        delete_unmanaged_channels = config.template_delete_unmanaged
        logger.info(f"  Configuration for deleting unmanaged items: {delete_unmanaged_channels}")

        if delete_unmanaged_channels:
            logger.info("  Checking for Discord channels not present in the template...")
            # Find Discord channel IDs present on the server but NOT processed (i.e., not matched or created from template)
            channels_to_delete_ids = set(live_channels.keys()) - processed_live_channel_ids
            logger.debug(f"    Found {len(channels_to_delete_ids)} live channel IDs not processed (candidates for deletion): {channels_to_delete_ids}")
            
            for discord_chan_id in channels_to_delete_ids:
                # Fetch the actual channel object
                channel_to_delete = discord_guild.get_channel(discord_chan_id)
                live_chan_data = live_channels.get(discord_chan_id) # Get data for logging
                chan_name_for_log = live_chan_data['name'] if live_chan_data else f"ID {discord_chan_id}"

                if channel_to_delete and not isinstance(channel_to_delete, nextcord.CategoryChannel): # Make sure not to delete categories here
                    logger.warning(f"    Discord channel '{chan_name_for_log}' (ID: {discord_chan_id}, Type: {channel_to_delete.type}) is not in the template. Deleting...")
                    try:
                        await channel_to_delete.delete(reason="Removing channel not defined in template")
                        logger.info(f"      Successfully deleted channel '{chan_name_for_log}'.")
                    except nextcord.Forbidden:
                        logger.error(f"      PERMISSION ERROR: Cannot delete channel '{chan_name_for_log}'.")
                    except nextcord.NotFound:
                            logger.warning(f"      Channel '{chan_name_for_log}' (ID: {discord_chan_id}) was already deleted.")
                    except nextcord.HTTPException as http_err:
                        logger.error(f"      HTTP ERROR deleting channel '{chan_name_for_log}': {http_err}")
                    except Exception as deletion_err:
                        logger.error(f"      UNEXPECTED ERROR deleting channel '{chan_name_for_log}': {deletion_err}", exc_info=True)
                elif channel_to_delete and isinstance(channel_to_delete, nextcord.CategoryChannel):
                        logger.debug(f"    Skipping category '{chan_name_for_log}' during channel deletion phase.")
                else:
                    # This case might happen if a channel was deleted manually during the sync
                    logger.warning(f"    Could not find Discord channel object with ID {discord_chan_id} ('{chan_name_for_log}') to delete. Already deleted?")
        # else: # Already logged above
            # logger.debug("  Deletion of unmanaged channels is disabled.")

        # ----------------------------------------------------------
        # 7. Process Categories (Delete from Discord if not in Template - Optional)
            # ----------------------------------------------------------
        # Use the same flag as for channels
        if delete_unmanaged_channels:
            logger.info("  Checking for Discord categories not present in the template...")
            # Compare all live category IDs with the ones we processed (found/created from template)
            categories_to_delete_ids = set(live_categories.keys()) - processed_live_category_ids
            logger.debug(f"    Found {len(categories_to_delete_ids)} live category IDs not processed (candidates for deletion): {categories_to_delete_ids}")

            for discord_cat_id in categories_to_delete_ids:
                # Fetch the actual category object
                category_to_delete = discord_guild.get_channel(discord_cat_id)
                live_cat_data = live_categories.get(discord_cat_id) # Get data for logging
                cat_name_for_log = live_cat_data['name'] if live_cat_data else f"ID {discord_cat_id}"

                if category_to_delete and isinstance(category_to_delete, nextcord.CategoryChannel):
                    # Check if category is empty FIRST
                    if not category_to_delete.channels: 
                        logger.warning(f"    Discord category '{cat_name_for_log}' (ID: {discord_cat_id}) is not in the template and is empty. Deleting...")
                        try:
                            await category_to_delete.delete(reason="Removing category not defined in template")
                            logger.info(f"      Successfully deleted category '{cat_name_for_log}'.")
                        except nextcord.Forbidden:
                            logger.error(f"      PERMISSION ERROR: Cannot delete category '{cat_name_for_log}'.")
                        except nextcord.NotFound:
                            logger.warning(f"      Category '{cat_name_for_log}' (ID: {discord_cat_id}) was already deleted.")
                        except nextcord.HTTPException as http_err:
                            logger.error(f"      HTTP ERROR deleting category '{cat_name_for_log}': {http_err}")
                        except Exception as deletion_err:
                            logger.error(f"      UNEXPECTED ERROR deleting category '{cat_name_for_log}': {deletion_err}", exc_info=True)
                    else:
                            logger.warning(f"    Discord category '{cat_name_for_log}' (ID: {discord_cat_id}) is not in the template BUT is NOT EMPTY. Skipping deletion.")
                            logger.debug(f"     Category '{cat_name_for_log}' contains channels: {[ch.name for ch in category_to_delete.channels]}")

                elif category_to_delete: 
                    logger.warning(f"    Found object for ID {discord_cat_id} ('{cat_name_for_log}') but it's not a CategoryChannel (Type: {type(category_to_delete)}). Skipping deletion.")
                else:
                    logger.warning(f"    Could not find Discord category object with ID {discord_cat_id} ('{cat_name_for_log}') to delete. Already deleted?")


        logger.info(f"[apply_template] Channel and Category Create/Update/Delete/Reorder logic complete. DB updates applied via session commit. Guild: {guild_id}.")

        # If we reach here without fatal errors, consider it successful
        # The session commit happens when the context manager in approve_guild exits.
        logger.info(f"[apply_template] Successfully applied template changes for guild {guild_id}.")
        return True

    except Exception as e:
        logger.error(f"[apply_template] Error applying template for guild {guild_id}: {e}", exc_info=True)
        # Rollback will be handled by the session_context in the caller (approve_guild)
        return False

# --- HELPER for Preparing Permissions ---
async def _prepare_permission_overwrites(
    self, # Added self back
    guild_roles: List[nextcord.Role], 
    template_perms_getter, # Function like cat_perm_repo.get_by_category_template_id
    template_element_id: int,
    log_prefix: str = "    " # For logging context
    ) -> Dict[nextcord.Role, nextcord.PermissionOverwrite]:
    """Fetches template permissions and prepares the overwrites dict for Discord API calls."""
    overwrites = {}
    try:
        template_perms = await template_perms_getter(template_element_id)
        if not template_perms:
            logger.debug(f"{log_prefix} No specific permissions found in template for element ID {template_element_id}.")
            return overwrites # Return empty dict

        # Create a lookup for guild roles by name for efficiency
        guild_roles_by_name = {role.name: role for role in guild_roles}

        for perm in template_perms:
            role = guild_roles_by_name.get(perm.role_name)
            if not role:
                logger.warning(f"{log_prefix} Role '{perm.role_name}' defined in template permissions not found on guild. Skipping permission.")
                continue

            # Create PermissionOverwrite object
            allow_value = perm.allow_permissions_bitfield if perm.allow_permissions_bitfield is not None else 0
            deny_value = perm.deny_permissions_bitfield if perm.deny_permissions_bitfield is not None else 0
            
            allow_perms = nextcord.Permissions(allow_value)
            deny_perms = nextcord.Permissions(deny_value)
            overwrites[role] = nextcord.PermissionOverwrite.from_pair(allow_perms, deny_perms)
            logger.debug(f"{log_prefix}  Prepared overwrite for role '{role.name}': Allow={allow_perms.value}, Deny={deny_perms.value}")

        logger.debug(f"{log_prefix} Prepared {len(overwrites)} permission overwrites for element ID {template_element_id}.")

    except Exception as prep_err:
            logger.error(f"{log_prefix} UNEXPECTED ERROR preparing permissions for element ID {template_element_id}: {prep_err}", exc_info=True)
            # Return empty dict on error to avoid applying partial/incorrect permissions
            return {}
            
    return overwrites

# --- HELPER for Applying Permissions (Edit Existing) ---
async def _apply_category_permissions(self, discord_category: nextcord.CategoryChannel, template_category_id: int, cat_perm_repo: GuildTemplateCategoryPermissionRepository) -> None:
    """Helper to apply permissions stored in the template to an existing Discord category."""
    log_prefix="    [Edit Cat]"
    logger.debug(f"{log_prefix} Applying permissions for category '{discord_category.name}' (Template ID: {template_category_id})")
    try:
        # Prepare overwrites using the helper
        overwrites_to_apply = await self._prepare_permission_overwrites(
                guild_roles=discord_category.guild.roles, 
                template_perms_getter=cat_perm_repo.get_by_category_template_id, 
                template_element_id=template_category_id,
                log_prefix=log_prefix
        )

        # Check if current overwrites differ significantly before editing? Maybe not needed, just apply.
        # current_overwrites = discord_category.overwrites

        if overwrites_to_apply: # Only edit if there are permissions to apply
                logger.info(f"{log_prefix} Setting {len(overwrites_to_apply)} permission overwrites for category '{discord_category.name}'")
                await discord_category.edit(overwrites=overwrites_to_apply, reason="Applying template permissions")
                logger.debug(f"{log_prefix}  Successfully applied permissions to category '{discord_category.name}'.")
        # else: # Already logged by helper
            # logger.debug(f"{log_prefix} No valid permissions found/prepared for category '{discord_category.name}'. No changes made.")

    except nextcord.Forbidden:
        logger.error(f"{log_prefix} PERMISSION ERROR: Cannot apply permissions to category '{discord_category.name}'. Check bot permissions.")
    except nextcord.HTTPException as http_err:
        logger.error(f"{log_prefix} HTTP ERROR applying permissions to category '{discord_category.name}': {http_err}")
    except Exception as perm_err:
        logger.error(f"{log_prefix} UNEXPECTED ERROR applying permissions to category '{discord_category.name}': {perm_err}", exc_info=True)

async def _apply_channel_permissions(
    self, # Added self back
    discord_channel: nextcord.abc.GuildChannel, # Use base GuildChannel type
    template_channel_id: int, 
    chan_perm_repo: GuildTemplateChannelPermissionRepository
) -> None:
    """Helper to apply permissions stored in the template to an existing Discord channel."""
    log_prefix="    [Edit Chan]"
    logger.debug(f"{log_prefix} Applying permissions for channel '{discord_channel.name}' (Template ID: {template_channel_id})")
    try:
        # Prepare overwrites using the helper
        overwrites_to_apply = await self._prepare_permission_overwrites(
                guild_roles=discord_channel.guild.roles, 
                template_perms_getter=chan_perm_repo.get_by_channel_template_id, 
                template_element_id=template_channel_id,
                log_prefix=log_prefix
        )

        # current_overwrites = discord_channel.overwrites # For comparison if needed

        if overwrites_to_apply:
                logger.info(f"{log_prefix} Setting {len(overwrites_to_apply)} permission overwrites for channel '{discord_channel.name}'")
                await discord_channel.edit(overwrites=overwrites_to_apply, reason="Applying template permissions")
                logger.debug(f"{log_prefix} Successfully applied permissions to channel '{discord_channel.name}'.")
        # else: # Logged by helper
            # logger.debug(f"{log_prefix} No valid permissions found/prepared for channel '{discord_channel.name}'. No changes made.")

    except nextcord.Forbidden:
        logger.error(f"{log_prefix} PERMISSION ERROR: Cannot apply permissions to channel '{discord_channel.name}'. Check bot permissions.")
    except nextcord.HTTPException as http_err:
        logger.error(f"{log_prefix} HTTP ERROR applying permissions to channel '{discord_channel.name}': {http_err}")
    except Exception as perm_err:
        logger.error(f"{log_prefix} UNEXPECTED ERROR applying permissions to channel '{discord_channel.name}': {perm_err}", exc_info=True)
# --- END HELPER FUNCTIONS ---

# Removed duplicate _check_and_create_channel - now using the implementation from check_structure.py
