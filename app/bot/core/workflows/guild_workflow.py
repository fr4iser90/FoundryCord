# app/bot/core/workflows/guild_workflow.py
import logging
from typing import Dict, Optional, List
from app.bot.core.workflows.base_workflow import BaseWorkflow, WorkflowStatus
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord.entities.guild_entity import GuildEntity
from app.shared.infrastructure.models.discord.entities.guild_user_entity import DiscordGuildUserEntity
from app.shared.infrastructure.models.discord.entities import GuildConfigEntity
from sqlalchemy.ext.asyncio import AsyncSession

# Import Domain interfaces (Repositories)
from app.shared.domain.repositories.discord.guild_config_repository import GuildConfigRepository
from app.shared.domain.repositories.guild_templates import (
    GuildTemplateRepository,
    GuildTemplateCategoryRepository,
    GuildTemplateChannelRepository,
    GuildTemplateCategoryPermissionRepository,
    GuildTemplateChannelPermissionRepository
)

# Import Infrastructure implementations
from app.shared.infrastructure.repositories.discord.guild_config_repository_impl import GuildConfigRepositoryImpl
from sqlalchemy import select
from datetime import datetime
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.infrastructure.repositories.discord.guild_repository_impl import GuildRepositoryImpl
from app.shared.infrastructure.repositories.guild_templates.guild_template_repository_impl import GuildTemplateRepositoryImpl
from app.shared.infrastructure.repositories.guild_templates.guild_template_category_repository_impl import GuildTemplateCategoryRepositoryImpl
from app.shared.infrastructure.repositories.guild_templates.guild_template_channel_repository_impl import GuildTemplateChannelRepositoryImpl
from app.shared.infrastructure.repositories.guild_templates.guild_template_category_permission_repository_impl import GuildTemplateCategoryPermissionRepositoryImpl
from app.shared.infrastructure.repositories.guild_templates.guild_template_channel_permission_repository_impl import GuildTemplateChannelPermissionRepositoryImpl
import nextcord
# --- NEW: Import DiscordQueryService --- 
from app.bot.application.services.discord.discord_query_service import DiscordQueryService

logger = get_bot_logger()

# String constants for access status
ACCESS_PENDING = "pending"
ACCESS_APPROVED = "approved"
ACCESS_REJECTED = "rejected"
ACCESS_SUSPENDED = "suspended"

class GuildWorkflow(BaseWorkflow):
    """Manages guild-related operations and synchronization"""
    
    def __init__(self, database_workflow: DatabaseWorkflow, bot):
        super().__init__("guild")
        self.bot = bot
        self.database_workflow = database_workflow
        self.requires_guild_approval = True
        self._guild_statuses: Dict[str, WorkflowStatus] = {}
        self._guild_access_statuses: Dict[str, str] = {}
        self.guild_repo = None
        self.guild_config_repo = None
        
        # Add database dependency
        self.add_dependency("database")
        
    async def initialize(self) -> bool:
        """Global initialization - minimal setup for all guilds"""
        logger.info("[Initialize] Initializing guild workflow")
        try:
            async with session_context() as session:
                guild_repo = GuildRepositoryImpl(session)
                guild_config_repo = GuildConfigRepositoryImpl(session)
                self.guild_repo = guild_repo
                self.guild_config_repo = guild_config_repo
                
                guilds = await guild_repo.get_all()
                logger.info(f"[Initialize] Found {len(guilds)} guilds in database")
                
                if not guilds and self.bot:
                    logger.info("[Initialize] No guilds in database, creating from Discord source...")
                    discord_guilds_list = self.bot.guilds
                    logger.info(f"[Initialize] Found {len(discord_guilds_list)} guilds from Discord API.")
                    
                    for discord_guild in discord_guilds_list:
                        guild_id_str = str(discord_guild.id)
                        logger.info(f"[Initialize] Processing discovered guild: {discord_guild.name} ({guild_id_str}) status: PENDING")
                        
                        guild_entity = await guild_repo.create_or_update(
                            guild_id=guild_id_str,
                            name=discord_guild.name,
                            access_status=ACCESS_PENDING,
                            member_count=discord_guild.member_count,
                            icon_url=str(discord_guild.icon.url) if discord_guild.icon else None,
                            owner_id=str(discord_guild.owner_id) if discord_guild.owner_id else None
                        )
                        if not guild_entity:
                            logger.error(f"[Initialize] Failed to create GuildEntity for {guild_id_str}. Skipping this guild.")
                            continue
                        
                        logger.info(f"[Initialize] Creating default GuildConfigEntity for {guild_id_str}...")
                        config_entity = await guild_config_repo.create_or_update(
                            guild_id=guild_id_str,
                            guild_name=discord_guild.name,
                            features={ 'dashboard': False, 'tasks': False, 'services': False },
                            active_template_id=None,
                            template_delete_unmanaged=False
                        )
                        if not config_entity:
                            logger.error(f"[Initialize] Failed to create GuildConfigEntity for {guild_id_str}. Approval might fail later!")
                        else:
                            logger.info(f"[Initialize] Default GuildConfigEntity created for {guild_id_str}.")
                            
                        guilds.append(guild_entity)

                    logger.info(f"[Initialize] Finished processing {len(discord_guilds_list)} discovered guilds.")
                
                for guild in guilds:
                    guild_id_str = guild.guild_id
                    logger.info(f"[Initialize] Processing status for guild {guild.name} ({guild_id_str}) - DB Status: {guild.access_status}")
                    current_status = guild.access_status or ACCESS_PENDING
                    self._guild_access_statuses[guild_id_str] = current_status
                    
                    if current_status == ACCESS_APPROVED:
                        self._guild_statuses[guild_id_str] = WorkflowStatus.ACTIVE
                        logger.info(f"[Initialize] Guild {guild_id_str} is already APPROVED.")
                        config = await guild_config_repo.get_by_guild_id(guild_id_str)
                        if not config:
                             logger.error(f"[Initialize] CRITICAL: GuildConfigEntity missing for APPROVED guild {guild_id_str}! Database state inconsistent.")
                             await guild_config_repo.create_or_update(guild_id=guild_id_str, guild_name=guild.name) # Attempt recovery
                    elif current_status == ACCESS_REJECTED:
                        self._guild_statuses[guild_id_str] = WorkflowStatus.UNAUTHORIZED
                        logger.info(f"[Initialize] Guild {guild_id_str} is REJECTED.")
                    elif current_status == ACCESS_SUSPENDED:
                        self._guild_statuses[guild_id_str] = WorkflowStatus.UNAUTHORIZED
                        logger.info(f"[Initialize] Guild {guild_id_str} is SUSPENDED.")
                    else: # PENDING
                        self._guild_statuses[guild_id_str] = WorkflowStatus.PENDING
                        if guild.access_status != ACCESS_PENDING:
                            logger.warning(f"[Initialize] Guild {guild_id_str} has unexpected status '{guild.access_status}'. Setting to PENDING.")
                            await guild_repo.update_access_status(guild_id_str, ACCESS_PENDING)
                        logger.info(f"[Initialize] Guild {guild_id_str} is PENDING approval.")
                    
            logger.info("[Initialize] Guild workflow initialization complete.")
            return True
        except Exception as e:
            logger.error(f"[Initialize] Error during guild workflow initialization: {e}", exc_info=True)
            return False

    async def on_guild_join(self, guild_id: str) -> bool:
        """Handle new guild joins"""
        logger.info(f"[on_guild_join] Processing new guild join: {guild_id}")
        try:
            async with session_context() as session:
                guild_repo = GuildRepositoryImpl(session)
                guild_config_repo = GuildConfigRepositoryImpl(session)
                
                discord_guild = self.bot.get_guild(int(guild_id))
                if not discord_guild:
                    logger.error(f"[on_guild_join] Could not find Discord guild object for {guild_id}")
                    return False
                
                logger.info(f"[on_guild_join] Creating/updating GuildEntity for {guild_id}...")
                guild = await guild_repo.create_or_update(
                    guild_id=guild_id,
                    name=discord_guild.name,
                    access_status=ACCESS_PENDING,
                    member_count=discord_guild.member_count,
                    icon_url=str(discord_guild.icon.url) if discord_guild.icon else None,
                    owner_id=str(discord_guild.owner_id) if discord_guild.owner_id else None
                )
                if not guild:
                     logger.error(f"[on_guild_join] Failed to create/update GuildEntity for {guild_id}.")
                     return False
                logger.info(f"[on_guild_join] GuildEntity created/updated successfully for {guild_id}.")
                
                logger.info(f"[on_guild_join] Attempting to create/update GuildConfigEntity for {guild_id}...")
                config_result = await guild_config_repo.create_or_update(
                    guild_id=guild_id,
                    guild_name=discord_guild.name,
                    features={
                        'dashboard': False,
                        'tasks': False,
                        'services': False
                    },
                    active_template_id=None,
                    template_delete_unmanaged=False
                )
                if not config_result:
                    logger.error(f"[on_guild_join] Failed to create/update GuildConfigEntity for {guild_id}.")
                    # This is a significant issue, might warrant returning False
                else:
                    logger.info(f"[on_guild_join] GuildConfigEntity create/update call completed successfully for {guild_id}.")

                self._guild_access_statuses[guild_id] = ACCESS_PENDING
                self._guild_statuses[guild_id] = WorkflowStatus.PENDING
                
                logger.info(f"[on_guild_join] Finished processing join for {guild_id}. Status set to PENDING.")
                return True
        except Exception as e:
            logger.error(f"[on_guild_join] Error handling guild join for {guild_id}: {e}", exc_info=True) 
            return False

    async def initialize_for_guild(self, guild_id: str) -> bool:
        """Initialize workflow for a specific guild"""
        logger.info(f"Initializing guild workflow for guild {guild_id}")
        
        try:
            # Update status to initializing
            self._guild_statuses[guild_id] = WorkflowStatus.INITIALIZING
            
            # Get guild from database using the correct repository
            async with session_context() as session:
                # Use GuildRepositoryImpl to get the GuildEntity which has access_status
                guild_repo = GuildRepositoryImpl(session) 
                guild = await guild_repo.get_by_id(guild_id)
                
                if not guild:
                    # Log the error accurately
                    logger.error(f"GuildEntity for {guild_id} not found in database")
                    self._guild_statuses[guild_id] = WorkflowStatus.FAILED
                    return False
                    
                # Store and check access status from GuildEntity
                self._guild_access_statuses[guild_id] = guild.access_status
                
                if guild.access_status == ACCESS_REJECTED:
                    logger.warning(f"Guild {guild_id} is REJECTED access")
                    self._guild_statuses[guild_id] = WorkflowStatus.UNAUTHORIZED
                    await self.enforce_access_control(guild)
                    return False
                    
                if guild.access_status != ACCESS_APPROVED:
                    logger.warning(f"Guild {guild_id} is PENDING approval")
                    self._guild_statuses[guild_id] = WorkflowStatus.PENDING
                    return False
                    
                # Perform full guild sync for approved guilds
                logger.info(f"Guild {guild_id} is APPROVED, performing full sync")
                success = await self.sync_guild(guild_id, sync_members_only=False)
                if not success:
                    self._guild_statuses[guild_id] = WorkflowStatus.FAILED
                    return False
                    
                # Mark as active if everything succeeded
                self._guild_statuses[guild_id] = WorkflowStatus.ACTIVE
                return True
            
        except Exception as e:
            logger.error(f"Error initializing guild {guild_id}: {e}")
            self._guild_statuses[guild_id] = WorkflowStatus.FAILED
            return False

    def get_guild_access_status(self, guild_id: str) -> str:
        """Get the current access status for a guild"""
        return self._guild_access_statuses.get(guild_id, ACCESS_PENDING)

    async def approve_guild(self, guild_id: str) -> bool:
        """Approve a guild, update its config, create initial template, and apply it."""
        try:
            async with session_context() as session:
                guild_repo = GuildRepositoryImpl(session)
                guild_config_repo = GuildConfigRepositoryImpl(session)
                
                # 1. Update Guild Status
                guild = await guild_repo.update_access_status(
                    guild_id=guild_id,
                    status=ACCESS_APPROVED
                )
                if not guild:
                    logger.error(f"Cannot approve guild {guild_id}: GuildEntity not found in database")
                    return False
                
                # 2. Fetch and Update GuildConfig (MUST exist)
                config = await guild_config_repo.get_by_guild_id(guild_id)
                if not config:
                    logger.error(f"CRITICAL FAILURE: GuildConfigEntity not found for guild {guild_id} during approval!")
                    return False

                logger.debug(f"Found existing GuildConfigEntity for guild {guild_id}. Updating features.")
                config_features = { 'dashboard': True, 'tasks': True, 'services': True }
                config.features = config_features
                logger.debug(f"Updated GuildConfigEntity features for guild {guild_id} (in session).")
                
                self._guild_access_statuses[guild_id] = ACCESS_APPROVED
                self._guild_statuses[guild_id] = WorkflowStatus.PENDING

                # 3. Create Initial Template
                logger.debug(f"Attempting to fetch nextcord.Guild object for ID: {guild_id}")
                discord_guild = self.bot.get_guild(int(guild_id))
                creation_success = False
                if discord_guild:
                    template_workflow = self.bot.workflow_manager.get_workflow("guild_template")
                    if template_workflow:
                        logger.info(f"Triggering template creation for approved guild {guild_id}")
                        try:
                            # Pass the session and the config object
                            creation_success = await template_workflow.create_template_for_guild(
                                discord_guild, 
                                guild_config=config, 
                                db_session=session # Use the same session
                            ) 
                            logger.info(f"Template creation result: {creation_success}")
                        except Exception as template_err:
                            logger.error(f"Error during template creation call: {template_err}", exc_info=True)
                    else:
                        logger.error("GuildTemplateWorkflow not found!")
                else:
                    logger.error(f"Could not find Discord guild object for ID {guild_id}.")

                # 4. Apply Template (if creation succeeded)
                apply_success = False
                if creation_success:
                    logger.info(f"Attempting to apply template for guild {guild_id}")
                    try:
                        # Pass the current session and the config object (modified in memory by create_template_for_guild)
                        apply_success = await self.apply_template(guild_id, config=config, session=session) 
                    except Exception as apply_err:
                        logger.error(f"Error during apply_template call for guild {guild_id}: {apply_err}", exc_info=True)
                        apply_success = False # Ensure apply_success is False on error
                    if apply_success:
                         logger.info(f"Successfully applied template for guild {guild_id}.")
                            # Update status to ACTIVE only after successful application
                         self._guild_statuses[guild_id] = WorkflowStatus.ACTIVE
                    else:
                            logger.error(f"Failed to apply template for guild {guild_id}. Workflow status remains {self.get_guild_status(guild_id)}.")
                else:
                    logger.warning(f"Skipping template application for guild {guild_id} due to creation failure.")

                # Commit all changes made within this session (status updates, config changes, template creation)
                # session_context handles commit on successful exit, rollback on error
                
                return True # Return True if approval process finished (regardless of apply success)

        except Exception as e:
            guild_id_str = str(guild_id)
            logger.error(f"Error approving guild {guild_id_str}: {e}", exc_info=True)
            # Ensure status is set to FAILED if not already set or PENDING/ACTIVE
            if guild_id_str not in self._guild_statuses or self._guild_statuses[guild_id_str] not in [WorkflowStatus.ACTIVE, WorkflowStatus.PENDING]:
                 self._guild_statuses[guild_id_str] = WorkflowStatus.FAILED
            return False

    async def deny_guild(self, guild_id: str) -> bool:
        """Deny a guild"""
        try:
            async with session_context() as session:
                # We need GuildEntity to update access status
                guild_repo = GuildRepositoryImpl(session)
                guild_entity = await guild_repo.get_by_id(guild_id) 

                if not guild_entity:
                    logger.error(f"Cannot deny guild {guild_id}: GuildEntity not found in database")
                    return False
                
                # Update access status on GuildEntity
                logger.info(f"Setting access_status to REJECTED for GuildEntity {guild_id}")
                guild_entity.access_status = ACCESS_REJECTED
                # Let the session commit handle the update

                # Fetch GuildConfig to enforce access control (leaving guild)
                guild_config_repo = GuildConfigRepositoryImpl(session)
                guild_config = await guild_config_repo.get_by_guild_id(guild_id)
                
                # Update local status
                self._guild_access_statuses[guild_id] = ACCESS_REJECTED
                self._guild_statuses[guild_id] = WorkflowStatus.UNAUTHORIZED
                
                # Enforce access control (uses GuildConfig object if found)
                await self.enforce_access_control(guild_config if guild_config else guild_entity) # Pass config if exists, else entity
                
                logger.info(f"Guild {guild_id} has been REJECTED")
                return True
                
        except Exception as e:
            logger.error(f"Error denying guild {guild_id}: {e}")
            return False

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
                        
                        new_discord_cat = await discord_guild.create_category(
                            name=template_cat.category_name,
                            # position=template_cat.position, # Position often less reliable on creation
                            overwrites=creation_overwrites, # Apply permissions now
                            reason=f"Applying template: {template.template_name}"
                        )
                        logger.info(f"      Successfully created category '{new_discord_cat.name}' (ID: {new_discord_cat.id}) at position {new_discord_cat.position}")

                        # Store mapping and mark as processed
                        created_or_found_discord_categories[template_cat.id] = new_discord_cat
                        processed_live_category_ids.add(new_discord_cat.id)

                    except nextcord.Forbidden:
                        logger.error(f"      PERMISSION ERROR: Cannot create category '{template_cat.category_name}'. Check bot permissions.")
                        # Decide if this is fatal - potentially skip this category and its channels? For now, continue.
                    except nextcord.HTTPException as http_err:
                        logger.error(f"      HTTP ERROR creating category '{template_cat.category_name}': {http_err}")
                    except Exception as creation_err:
                         logger.error(f"      UNEXPECTED ERROR creating category '{template_cat.category_name}': {creation_err}", exc_info=True)

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
                             potential_match = discord_guild.get_channel(discord_chan_id)
                             if potential_match and str(potential_match.type) == template_chan.channel_type:
                                existing_discord_chan_object = potential_match
                                logger.debug(f"    Found potential match by name and parent: {existing_discord_chan_object.name} ({existing_discord_chan_object.id})")
                                # --- Update DB discord_channel_id (since we found it by name) --- 
                                if template_chan.discord_channel_id != str(existing_discord_chan_object.id):
                                    logger.info(f"      Updating DB discord_id for template channel {template_chan.id} from {template_chan.discord_channel_id} to {existing_discord_chan_object.id}")
                                    template_chan.discord_channel_id = str(existing_discord_chan_object.id)
                                    # Session commit will handle saving this change later
                                # -------------------------------------
                             else:
                                 logger.warning(f"    Name match found for '{template_chan.channel_name}' but type is wrong ({potential_match.type if potential_match else 'None'}) vs template ({template_chan.channel_type}). Treating as non-existent.")
                        else:
                             logger.error(f"    Live channel data found for name/parent match of '{template_chan.channel_name}' but is missing 'id'. Data inconsistency from query service?")

                # --- Update or Create Channel ---
                if existing_discord_chan_object:
                    processed_live_channel_ids.add(existing_discord_chan_object.id)
                    logger.info(f"    Channel '{template_chan.channel_name}' already exists (ID: {existing_discord_chan_object.id}). Checking for updates...")
                    
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
                    await self._apply_channel_permissions(existing_discord_chan_object, template_chan.id, chan_perm_repo)

                else:
                    # --- Create Channel ---
                    logger.info(f"    Channel '{template_chan.channel_name}' does not exist or match type/parent. Creating...")
                    
                    # Prepare overwrites BEFORE creation
                    creation_overwrites = await self._prepare_permission_overwrites(
                        guild_roles=discord_guild.roles, 
                        template_perms_getter=chan_perm_repo.get_by_channel_template_id, 
                        template_element_id=template_chan.id,
                        log_prefix="      [Create Chan]"
                    )

                    creation_kwargs = {
                         'name': template_chan.channel_name,
                         'category': target_discord_category,
                         # 'position': template_chan.position, # Position often less reliable on creation
                         'overwrites': creation_overwrites, # Apply permissions now
                         'reason': f"Applying template: {template.template_name}"
                    }
                    # Add type-specific args
                    if template_chan.channel_type == 'text':
                        creation_kwargs.update({
                            'topic': template_chan.topic,
                            'slowmode_delay': template_chan.slowmode_delay,
                            'nsfw': template_chan.is_nsfw
                        })
                        channel_creator = discord_guild.create_text_channel
                    elif template_chan.channel_type == 'voice':
                         creation_kwargs.update({
                             # Add bitrate, user_limit if stored in template
                         })
                         channel_creator = discord_guild.create_voice_channel
                    elif template_chan.channel_type == 'stage_voice': # Check nextcord's exact type string if different
                         creation_kwargs.update({
                            # Add stage specific args if needed
                         })
                         channel_creator = discord_guild.create_stage_channel
                    elif template_chan.channel_type == 'forum':
                          creation_kwargs.update({
                            'topic': template_chan.topic,
                            # 'slowmode_delay': template_chan.slowmode_delay, # Forum might not have slowmode? Check API
                            'nsfw': template_chan.is_nsfw
                            # Add tags etc. if stored in template
                         })
                          channel_creator = discord_guild.create_forum # Use create_forum
                    else:
                        logger.error(f"      Unsupported channel type '{template_chan.channel_type}' in template. Cannot create.")
                        continue # Skip this channel

                    try:
                        new_discord_chan = await channel_creator(**creation_kwargs)
                        logger.info(f"      Successfully created {template_chan.channel_type} channel '{new_discord_chan.name}' (ID: {new_discord_chan.id})")
                        
                        # --- Update DB discord_channel_id --- 
                        logger.info(f"      Updating DB discord_id for template channel {template_chan.id} to {new_discord_chan.id}")
                        template_chan.discord_channel_id = str(new_discord_chan.id)
                        # Session commit will handle saving this change later
                        # -------------------------------------

                        processed_live_channel_ids.add(new_discord_chan.id) # Track newly created channel ID

                    except nextcord.Forbidden:
                        logger.error(f"      PERMISSION ERROR: Cannot create {template_chan.channel_type} channel '{template_chan.channel_name}'. Check bot permissions.")
                    except nextcord.HTTPException as http_err:
                        logger.error(f"      HTTP ERROR creating {template_chan.channel_type} channel '{template_chan.channel_name}': {http_err}")
                    except Exception as creation_err:
                         logger.error(f"      UNEXPECTED ERROR creating {template_chan.channel_type} channel '{template_chan.channel_name}': {creation_err}", exc_info=True)

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
            # else: # Already logged above
                 # logger.debug("  Deletion of unmanaged categories is disabled (same flag as channels).")
            # --- END CATEGORY DELETION ---

            # ----------------------------------------------------------
            # 8. Final Reordering using Bulk Update
            # ----------------------------------------------------------
            logger.info("  Attempting final reordering of channels and categories...")
            try:
                # Prepare the positions data for the bulk update API
                # This needs to reflect the desired order based *only* on template items that now exist on Discord
                final_positions_data = [] # List of tuples: (channel_id, position_index)
                current_pos = 0

                # Get all relevant template channels and categories again, sorted correctly
                
                # Uncategorized channels first, sorted by template position
                uncategorized_chans = sorted(
                    [ch for ch in template_channels if ch.parent_category_template_id is None],
                    key=lambda c: c.position
                )
                for template_chan in uncategorized_chans:
                    if template_chan.discord_channel_id: # Only include channels that now exist on Discord
                        final_positions_data.append( (int(template_chan.discord_channel_id), current_pos) )
                        current_pos += 1
                    else:
                        logger.warning(f"    Skipping uncategorized channel '{template_chan.channel_name}' in final reorder (no Discord ID found/set).")

                # Then categories and their channels, sorted by template position
                sorted_cats = sorted(template_categories, key=lambda c: c.position)
                for template_cat in sorted_cats:
                    # Get the corresponding Discord category object (should exist if processed)
                    discord_category = created_or_found_discord_categories.get(template_cat.id)
                    if discord_category:
                        final_positions_data.append( (discord_category.id, current_pos) )
                        current_pos += 1
                        
                        # Channels within this category, sorted by template position
                        categorized_chans = sorted(
                            [ch for ch in template_channels if ch.parent_category_template_id == template_cat.id],
                            key=lambda c: c.position
                        )
                        for template_chan in categorized_chans:
                            if template_chan.discord_channel_id: # Only include channels that now exist
                                final_positions_data.append( (int(template_chan.discord_channel_id), current_pos) )
                                current_pos += 1
                            else:
                                 logger.warning(f"    Skipping categorized channel '{template_chan.channel_name}' in final reorder (no Discord ID found/set).")
                    else:
                         logger.warning(f"    Skipping category '{template_cat.category_name}' and its channels in final reorder (Discord category object not found in map).")

                # Convert list of tuples to the dictionary format required by nextcord
                final_positions_dict = {item[0]: item[1] for item in final_positions_data}

                # Call the bulk update function
                if final_positions_dict:
                    logger.debug(f"    Prepared final positions dict (first 5): {dict(list(final_positions_dict.items())[:5])}") # Log snippet
                    await discord_guild.edit_channel_positions(positions=final_positions_dict)
                    logger.info("    Successfully applied final channel and category order.")
                else:
                    logger.info("    No channels/categories with Discord IDs found to reorder.")

            except nextcord.Forbidden:
                logger.error("    PERMISSION ERROR during final reordering. Check bot permissions for channel management.")
                # Decide if this should be a fatal error for the apply process - maybe not?
            except nextcord.HTTPException as http_err:
                logger.error(f"    HTTP ERROR during final reordering: {http_err}")
            except Exception as reorder_err:
                logger.error(f"    UNEXPECTED ERROR during final reordering: {reorder_err}", exc_info=True)
            # --- END FINAL REORDERING ---

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
        self, 
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
        self, 
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

    async def sync_guild(self, guild_id: str, sync_members_only: bool = True) -> bool:
        """Synchronize guild data with Discord"""
        logger.info(f"Syncing guild {guild_id} (members_only={sync_members_only})")
        try:
            discord_guild = self.bot.get_guild(int(guild_id))
            if not discord_guild:
                logger.error(f"Could not find Discord guild {guild_id}")
                return False
                
            async with session_context() as session:
                guild_repo = GuildRepositoryImpl(session)
                db_guild = await guild_repo.get_by_id(guild_id)
                if not db_guild:
                    logger.error(f"Could not find GuildEntity {guild_id} in database") 
                    return False
                    
                if not sync_members_only:
                    db_guild.name = discord_guild.name
                    db_guild.icon_url = str(discord_guild.icon.url) if discord_guild.icon else None 
                    db_guild.member_count = discord_guild.member_count
                    db_guild.owner_id = str(discord_guild.owner_id) if discord_guild.owner_id else None 
                    await guild_repo.update(db_guild) # Use update for existing entity
                    logger.info(f"Updated guild metadata for {guild_id}")
                    
                # Sync members if user_workflow exists
                user_workflow = self.bot.workflow_manager.get_workflow("user")
                if user_workflow:
                    await user_workflow.sync_guild_members(discord_guild)
                else:
                    logger.warning("User workflow not available for member sync")
                return True
        except Exception as e:
            logger.error(f"Error syncing guild {guild_id}: {e}")
            return False
            
    async def enforce_access_control(self, guild_or_config) -> None:
        """Enforce access control based on guild status. Kicks bot if REJECTED/SUSPENDED."""
        # Determine guild_id and access_status from either GuildEntity or GuildConfigEntity
        guild_id = None
        access_status = None
        if isinstance(guild_or_config, GuildConfigEntity):
            guild_id = guild_or_config.guild_id
            # Need to fetch GuildEntity to get reliable current access_status
            async with session_context() as temp_session:
                 repo = GuildRepositoryImpl(temp_session)
                 entity = await repo.get_by_id(guild_id)
                 if entity: access_status = entity.access_status
        elif isinstance(guild_or_config, GuildEntity):
             guild_id = guild_or_config.guild_id
             access_status = guild_or_config.access_status
        else:
             logger.error(f"enforce_access_control called with invalid type: {type(guild_or_config)}")
             return

        if not guild_id or not access_status:
             logger.error(f"Could not determine guild_id or access_status for enforcement: {guild_or_config}")
             return
             
        if access_status in [ACCESS_REJECTED, ACCESS_SUSPENDED]:
            logger.info(f"Enforcing access control for guild {guild_id} with status {access_status}")
            try:
                discord_guild = self.bot.get_guild(int(guild_id))
                if discord_guild:
                    await discord_guild.leave()
                    logger.info(f"Left guild {guild_id} due to {access_status} status")
                else:
                    logger.warning(f"Cannot leave guild {guild_id} for enforcement: Bot is not currently in this guild.")
                    
            except nextcord.Forbidden:
                 logger.error(f"PERMISSION ERROR trying to leave guild {guild_id} for enforcement.")
            except Exception as e:
                logger.error(f"Error enforcing access control for guild {guild_id}: {e}")
                
    def get_guild_status(self, guild_id: str) -> WorkflowStatus:
        """Get the current status of the workflow for a specific guild"""
        return self._guild_statuses.get(guild_id, WorkflowStatus.PENDING)
        
    async def disable_for_guild(self, guild_id: str) -> None:
        """Disable workflow for a specific guild"""
        logger.info(f"Disabling guild workflow for guild {guild_id}")
        self._guild_statuses[guild_id] = WorkflowStatus.DISABLED
        
        # Update status in DB? Maybe not needed, depends on use case.
        # async with session_context() as session:
        #     guild_repo = GuildRepositoryImpl(session)
        #     await guild_repo.update_access_status(guild_id, SOME_DISABLED_STATUS) # Need a DB status for disabled?
                
    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup resources for a specific guild"""
        logger.info(f"Cleaning up guild workflow for guild {guild_id}")
        if guild_id in self._guild_statuses:
            del self._guild_statuses[guild_id]
        if guild_id in self._guild_access_statuses:
            del self._guild_access_statuses[guild_id]
            
    async def cleanup(self) -> None:
        """Global cleanup"""
        logger.info("Cleaning up guild workflow")
        self._guild_statuses.clear()
        self._guild_access_statuses.clear()