# app/bot/core/workflows/guild_workflow.py
import logging
from typing import Dict, Optional, List
from app.bot.core.workflows.base_workflow import BaseWorkflow, WorkflowStatus
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord.entities.guild_entity import GuildEntity
from app.shared.infrastructure.models.discord.entities.guild_user_entity import DiscordGuildUserEntity

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
        logger.info("Initializing guild workflow")
        try:
            # Basic setup and validation
            async with session_context() as session:
                # Initialize repositories
                self.guild_repo = GuildRepositoryImpl(session)
                self.guild_config_repo = GuildConfigRepositoryImpl(session)
                
                # Get all guilds
                guilds = await self.guild_repo.get_all()
                logger.info(f"Found {len(guilds)} guilds in database")
                
                # If no guilds in database, create them from Discord
                if not guilds and self.bot:
                    logger.info("No guilds in database, creating from Discord")
                    for discord_guild in self.bot.guilds:
                        logger.info(f"Creating guild {discord_guild.name} ({discord_guild.id}) as PENDING")
                        guild = await self.guild_repo.create_or_update(
                            guild_id=str(discord_guild.id),
                            name=discord_guild.name,
                            access_status=ACCESS_PENDING,
                            member_count=discord_guild.member_count,
                            icon_url=str(discord_guild.icon.url) if discord_guild.icon else None,
                            owner_id=str(discord_guild.owner_id) if discord_guild.owner_id else None
                        )
                        guilds.append(guild)
                
                for guild in guilds:
                    logger.info(f"Processing guild {guild.name} ({guild.guild_id}) with status {guild.access_status}")
                    
                    # Get current access status or set to PENDING if none
                    current_status = guild.access_status or ACCESS_PENDING
                    
                    # Store access status
                    self._guild_access_statuses[guild.guild_id] = current_status
                    
                    # Set workflow status based on access status
                    if current_status == ACCESS_APPROVED:
                        self._guild_statuses[guild.guild_id] = WorkflowStatus.ACTIVE
                        logger.info(f"Guild {guild.guild_id} is APPROVED")
                        
                        # Ensure config exists for approved guilds
                        config = await self.guild_config_repo.get_by_guild_id(guild.guild_id)
                        if not config:
                            await self.guild_config_repo.create_or_update(
                                guild_id=guild.guild_id,
                                guild_name=guild.name
                            )
                            
                    elif current_status == ACCESS_REJECTED:
                        self._guild_statuses[guild.guild_id] = WorkflowStatus.UNAUTHORIZED
                        logger.info(f"Guild {guild.guild_id} is REJECTED")
                    elif current_status == ACCESS_SUSPENDED:
                        self._guild_statuses[guild.guild_id] = WorkflowStatus.UNAUTHORIZED
                        logger.info(f"Guild {guild.guild_id} is SUSPENDED")
                        await self.enforce_access_control(guild)
                    else:
                        # For PENDING or unknown status
                        self._guild_statuses[guild.guild_id] = WorkflowStatus.PENDING
                        if guild.access_status != ACCESS_PENDING:
                            logger.info(f"Setting guild {guild.guild_id} to PENDING")
                            await self.guild_repo.update_access_status(
                                guild.guild_id, 
                                ACCESS_PENDING
                            )
                        logger.info(f"Guild {guild.guild_id} is waiting for approval (PENDING)")
                    
            return True
        except Exception as e:
            logger.error(f"Error in guild workflow initialization: {e}")
            logger.exception("Full traceback:")
            return False

    async def on_guild_join(self, guild_id: str) -> bool:
        """Handle new guild joins"""
        logger.info(f"Processing new guild join: {guild_id}")
        try:
            async with session_context() as session:
                # Initialize repositories if needed
                if not self.guild_repo:
                    self.guild_repo = GuildRepositoryImpl(session)
                if not self.guild_config_repo:
                    self.guild_config_repo = GuildConfigRepositoryImpl(session)
                
                # Get Discord guild
                discord_guild = self.bot.get_guild(int(guild_id))
                if not discord_guild:
                    logger.error(f"Could not find Discord guild {guild_id}")
                    return False
                
                # Create or update guild with PENDING status
                guild = await self.guild_repo.create_or_update(
                    guild_id=guild_id,
                    name=discord_guild.name,
                    access_status=ACCESS_PENDING,
                    member_count=discord_guild.member_count,
                    icon_url=str(discord_guild.icon.url) if discord_guild.icon else None,
                    owner_id=str(discord_guild.owner_id) if discord_guild.owner_id else None
                )
                
                # Create default config with relevant feature flags set to False
                await self.guild_config_repo.create_or_update(
                    guild_id=guild_id,
                    guild_name=discord_guild.name,
                    features={
                        'dashboard': False,
                        'tasks': False,
                        'services': False
                    }
                )
                
                # Update local status
                self._guild_access_statuses[guild_id] = ACCESS_PENDING
                self._guild_statuses[guild_id] = WorkflowStatus.PENDING
                
                logger.info(f"New guild {guild_id} set to PENDING approval")
                return True
                
        except Exception as e:
            logger.error(f"Error handling guild join for {guild_id}: {e}")
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
        """Approve a guild"""
        try:
            async with session_context() as session:
                if not self.guild_repo:
                    self.guild_repo = GuildRepositoryImpl(session)
                if not self.guild_config_repo:
                    self.guild_config_repo = GuildConfigRepositoryImpl(session)
                
                # Update guild status
                guild = await self.guild_repo.update_access_status(
                    guild_id=guild_id,
                    status=ACCESS_APPROVED
                )
                
                if not guild:
                    logger.error(f"Cannot approve guild {guild_id}: not found in database")
                    return False
                
                # Ensure config exists and enable relevant features
                config = await self.guild_config_repo.get_by_guild_id(guild_id)
                config_features = {
                    'dashboard': True,
                    'tasks': True,
                    'services': True
                }

                if not config:
                    await self.guild_config_repo.create_or_update(
                        guild_id=guild_id,
                        guild_name=guild.name,
                        features=config_features
                    )
                    logger.debug(f"Created missing GuildConfigEntity for approved guild {guild_id} with features enabled.")
                else:
                    # Update existing config with enabled features
                    await self.guild_config_repo.create_or_update(
                        guild_id=guild_id,
                        guild_name=guild.name,
                        features=config_features
                    )
                    logger.debug(f"Updated existing GuildConfigEntity for approved guild {guild_id} with features enabled.")
                
                # Update local status
                self._guild_access_statuses[guild_id] = ACCESS_APPROVED
                self._guild_statuses[guild_id] = WorkflowStatus.PENDING

                # --- Trigger Template Creation --- 
                logger.debug(f"Attempting to fetch nextcord.Guild object for ID: {guild_id}")
                discord_guild = self.bot.get_guild(int(guild_id))
                
                if discord_guild:
                    logger.debug(f"Found nextcord.Guild object: {discord_guild.name}")
                    # Get the template workflow and execute template creation
                    template_workflow = self.bot.workflow_manager.get_workflow("guild_template")
                    if template_workflow:
                        logger.info(f"Triggering template creation for approved guild {guild_id}")
                        try:
                            creation_success = await template_workflow.create_template_for_guild(discord_guild)
                            logger.info(f"Template creation result for guild {guild_id}: {creation_success}")
                        except Exception as template_err:
                            logger.error(f"Error during template_workflow.create_template_for_guild call for {guild_id}: {template_err}", exc_info=True)
                            creation_success = False # Ensure creation_success is defined
                            # Decide if we should still proceed with initialization
                    else:
                        logger.error("GuildTemplateWorkflow not found in manager!")
                        creation_success = False # Ensure creation_success is defined
                else:
                    logger.error(f"Could not find Discord guild object for ID {guild_id} in bot cache. Cannot create template.")
                    creation_success = False # Ensure creation_success is defined
                # --- End Trigger --- 

                # --- Apply Template --- 
                if creation_success: # Only attempt to apply if creation was successful (or if we decide to apply existing)
                    logger.info(f"Attempting to apply the created/existing template for guild {guild_id}")
                    apply_success = await self.apply_template(guild_id)
                    if apply_success:
                         logger.info(f"Successfully applied template for guild {guild_id}.")
                         # Final status update can happen here or within apply_template
                         self._guild_statuses[guild_id] = WorkflowStatus.ACTIVE
                    else:
                         logger.error(f"Failed to apply template for guild {guild_id}. Workflow remains PENDING.")
                         # Keep status as PENDING if apply fails, or set to FAILED?
                else:
                    logger.warning(f"Skipping template application for guild {guild_id} due to creation failure or lack of guild object.")
                # --- End Apply --- 

                return True
                
        except Exception as e:
            logger.error(f"Error approving guild {guild_id}: {e}", exc_info=True)
            return False

    async def deny_guild(self, guild_id: str) -> bool:
        """Deny a guild"""
        try:
            async with session_context() as session:
                guild_config_repo = GuildConfigRepositoryImpl(session)
                guild = await guild_config_repo.get_by_guild_id(guild_id)
                
                if not guild:
                    logger.error(f"Cannot deny guild {guild_id}: not found in database")
                    return False
                
                # Update access status
                guild.access_status = ACCESS_REJECTED
                await guild_config_repo.update(guild)
                
                # Update local status
                self._guild_access_statuses[guild_id] = ACCESS_REJECTED
                self._guild_statuses[guild_id] = WorkflowStatus.UNAUTHORIZED
                
                # Enforce access control
                await self.enforce_access_control(guild)
                
                logger.info(f"Guild {guild_id} has been REJECTED")
                return True
                
        except Exception as e:
            logger.error(f"Error denying guild {guild_id}: {e}")
            return False

    async def apply_template(self, guild_id: str) -> bool:
        """Applies the stored template structure to the Discord guild."""
        logger.info(f"Attempting to apply template for guild {guild_id}")
        discord_guild = self.bot.get_guild(int(guild_id))
        if not discord_guild:
            logger.error(f"[apply_template] Could not find Discord guild {guild_id}")
            return False

        try:
            async with session_context() as session:
                # Instantiate repositories
                template_repo = GuildTemplateRepositoryImpl(session)
                guild_config_repo = GuildConfigRepositoryImpl(session)
                cat_repo = GuildTemplateCategoryRepositoryImpl(session)
                chan_repo = GuildTemplateChannelRepositoryImpl(session)
                cat_perm_repo = GuildTemplateCategoryPermissionRepositoryImpl(session)
                chan_perm_repo = GuildTemplateChannelPermissionRepositoryImpl(session)

                # --- NEW: Instantiate Discord Query Service ---
                discord_query_service = DiscordQueryService(self.bot)
                # -------------------------------------------

                # 1. Load Template Data
                # --- NEUE LOGIK ZUM LADEN DES AKTIVEN TEMPLATES ---
                logger.debug(f"[apply_template] Fetching GuildConfig for guild {guild_id} to find active template.")
                guild_config = await guild_config_repo.get_by_guild_id(guild_id)
                if not guild_config or guild_config.active_template_id is None:
                    logger.warning(f"[apply_template] No active template configured for guild {guild_id} in GuildConfig. Cannot apply.")
                    return False

                active_template_id = guild_config.active_template_id
                logger.info(f"[apply_template] Found active template ID from GuildConfig: {active_template_id}")

                template = await template_repo.get_by_id(active_template_id)
                if not template:
                    # This case might indicate inconsistent data (active_template_id points to non-existent template)
                    logger.error(f"[apply_template] Active template ID {active_template_id} (from GuildConfig) not found in GuildTemplate table for guild {guild_id}. Data inconsistency?")
                    return False
                # --- ENDE NEUE LOGIK ---

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
                live_categories = live_guild_data.get('categories', {})
                live_channels = live_guild_data.get('channels', {})

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

                # Sort template categories by position for correct creation order
                sorted_template_categories = sorted(template_categories, key=lambda c: c.position)

                for template_cat in sorted_template_categories:
                    logger.debug(f"  Processing template category: '{template_cat.category_name}' (Pos: {template_cat.position})")
                    
                    existing_discord_cat_id = discord_categories_by_name.get(template_cat.category_name)
                    existing_discord_cat_object = None
                    if existing_discord_cat_id:
                         existing_discord_cat_object = discord_guild.get_channel(existing_discord_cat_id) # Fetch the object

                    if existing_discord_cat_object and isinstance(existing_discord_cat_object, nextcord.CategoryChannel): 
                        logger.info(f"    Category '{template_cat.category_name}' already exists on Discord (ID: {existing_discord_cat_object.id}).")
                        # TODO: Update position? 
                        # if existing_discord_cat_object.position != template_cat.position: ... existing_discord_cat_object.edit(position=...) ...
                        
                        # Apply permissions 
                        await self._apply_category_permissions(existing_discord_cat_object, template_cat.id, cat_perm_repo)
                        
                        # Store mapping
                        created_or_found_discord_categories[template_cat.id] = existing_discord_cat_object

                    else:
                        logger.info(f"    Category '{template_cat.category_name}' does not exist. Creating...")
                        try:
                            # TODO: Apply overwrites during creation if possible?
                            new_discord_cat = await discord_guild.create_category(
                                name=template_cat.category_name,
                                position=template_cat.position, # Attempt to set position on creation
                                reason=f"Applying template: {template.template_name}"
                            )
                            logger.info(f"      Successfully created category '{new_discord_cat.name}' (ID: {new_discord_cat.id}) at position {new_discord_cat.position}")
                            
                            # Apply permissions after creation
                            await self._apply_category_permissions(new_discord_cat, template_cat.id, cat_perm_repo)

                            # Store mapping
                            created_or_found_discord_categories[template_cat.id] = new_discord_cat

                        except nextcord.Forbidden:
                            logger.error(f"      PERMISSION ERROR: Cannot create category '{template_cat.category_name}'. Check bot permissions.")
                            # Decide how to handle: continue? rollback? stop?
                        except nextcord.HTTPException as http_err:
                            logger.error(f"      HTTP ERROR creating category '{template_cat.category_name}': {http_err}")
                        except Exception as creation_err:
                             logger.error(f"      UNEXPECTED ERROR creating category '{template_cat.category_name}': {creation_err}", exc_info=True)

                # ----------------------------------------------------------
                # 4. Process Channels (Create/Update/Delete)
                # ----------------------------------------------------------
                logger.info("Processing channels...")
                
                # --- Create Lookups ---
                # Map template channel ID -> template channel entity
                template_channels_by_id = {chan.id: chan for chan in template_channels}
                
                # Map (name, parent_template_id) -> template channel entity (for matching channels without discord_id)
                template_channels_by_name_parent = {(chan.channel_name, chan.parent_category_template_id): chan for chan in template_channels}
                
                # Map live Discord channel ID -> live channel data dict (from DiscordQueryService)
                # live_channels = live_guild_data.get('channels', {}) # Already defined

                # Map (name, parent_discord_id) -> live channel data dict
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
                        target_discord_category = created_or_found_discord_categories.get(template_chan.parent_category_template_id)
                        if not target_discord_category:
                            logger.warning(f"    Parent category (Template ID: {template_chan.parent_category_template_id}) not found or created on Discord for channel '{template_chan.channel_name}'. Will create channel without parent.")
                    
                    target_parent_discord_id = target_discord_category.id if target_discord_category else None

                    # --- Try to find existing Discord channel ---
                    existing_discord_chan_object = None
                    # 1. Try matching by known Discord ID (if set previously)
                    if template_chan.discord_channel_id:
                         potential_match = discord_guild.get_channel(int(template_chan.discord_channel_id))
                         # Verify it's the correct type (or handle type changes?)
                         if potential_match and str(potential_match.type) == template_chan.channel_type:
                             existing_discord_chan_object = potential_match
                             logger.debug(f"    Found potential match by DB discord_channel_id: {existing_discord_chan_object.name} ({existing_discord_chan_object.id})")
                         else:
                              logger.warning(f"    DB discord_channel_id {template_chan.discord_channel_id} for '{template_chan.channel_name}' points to a non-existent channel or channel of wrong type ({potential_match.type if potential_match else 'None'}). Ignoring ID.")
                              # Reset the ID in DB? For now, just proceed to name matching.
                              # await chan_repo.update(template_chan, discord_channel_id=None) # Example

                    # 2. If no match by ID, try matching by name and parent
                    if not existing_discord_chan_object:
                        live_match_data = live_channels_by_name_parent.get((template_chan.channel_name, target_parent_discord_id))
                        if live_match_data:
                            # Fetch the actual channel object using the ID from live data
                            # Find the key (channel_id) corresponding to the matched value (live_match_data)
                            discord_chan_id = None
                            for chan_id, chan_data in live_channels.items():
                                if chan_data == live_match_data:
                                     discord_chan_id = chan_id
                                     break
                            
                            if discord_chan_id:
                                 potential_match = discord_guild.get_channel(discord_chan_id)
                                 if potential_match and str(potential_match.type) == template_chan.channel_type:
                                    existing_discord_chan_object = potential_match
                                    logger.debug(f"    Found potential match by name and parent: {existing_discord_chan_object.name} ({existing_discord_chan_object.id})")
                                    # --- Update DB discord_channel_id --- 
                                    if template_chan.discord_channel_id != str(existing_discord_chan_object.id):
                                        logger.info(f"      Updating DB discord_id for template channel {template_chan.id} from {template_chan.discord_channel_id} to {existing_discord_chan_object.id}")
                                        template_chan.discord_channel_id = str(existing_discord_chan_object.id)
                                        # Session commit will handle saving this change
                                    # -------------------------------------

                    # --- Update or Create Channel ---
                    if existing_discord_chan_object:
                        processed_live_channel_ids.add(existing_discord_chan_object.id)
                        logger.info(f"    Channel '{template_chan.channel_name}' already exists (ID: {existing_discord_chan_object.id}). Checking for updates...")
                        
                        # --- Check for updates ---
                        updates_needed = {}
                        if existing_discord_chan_object.name != template_chan.channel_name: # Note: Name match was primary way to find it if ID was missing
                             updates_needed['name'] = template_chan.channel_name
                        if existing_discord_chan_object.position != template_chan.position:
                             updates_needed['position'] = template_chan.position
                        if getattr(existing_discord_chan_object, 'topic', None) != template_chan.topic:
                            updates_needed['topic'] = template_chan.topic # Only for text/forum
                        if getattr(existing_discord_chan_object, 'nsfw', False) != template_chan.is_nsfw:
                             updates_needed['nsfw'] = template_chan.is_nsfw # Only for text/voice/forum/stage
                        if isinstance(existing_discord_chan_object, (nextcord.TextChannel, nextcord.ForumChannel)):
                            if existing_discord_chan_object.slowmode_delay != template_chan.slowmode_delay:
                                updates_needed['slowmode_delay'] = template_chan.slowmode_delay
                        if existing_discord_chan_object.category != target_discord_category: # Compare objects directly
                             updates_needed['category'] = target_discord_category # Move category

                        if updates_needed:
                            try:
                                logger.info(f"      Updating channel '{existing_discord_chan_object.name}' ({existing_discord_chan_object.id}) with changes: {updates_needed}")
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
                        logger.info(f"    Channel '{template_chan.channel_name}' does not exist. Creating...")
                        creation_kwargs = {
                             'name': template_chan.channel_name,
                             'category': target_discord_category,
                             'position': template_chan.position,
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
                                'slowmode_delay': template_chan.slowmode_delay,
                                'nsfw': template_chan.is_nsfw
                                # Add tags etc. if stored in template
                             })
                              channel_creator = discord_guild.create_forum
                        else:
                            logger.error(f"      Unsupported channel type '{template_chan.channel_type}' in template. Cannot create.")
                            continue # Skip this channel

                        try:
                            new_discord_chan = await channel_creator(**creation_kwargs)
                            logger.info(f"      Successfully created {template_chan.channel_type} channel '{new_discord_chan.name}' (ID: {new_discord_chan.id})")
                            
                            # Apply permissions
                            await self._apply_channel_permissions(new_discord_chan, template_chan.id, chan_perm_repo)

                            # --- Update DB discord_channel_id --- 
                            logger.info(f"      Updating DB discord_id for template channel {template_chan.id} to {new_discord_chan.id}")
                            template_chan.discord_channel_id = str(new_discord_chan.id)
                            # Session commit will handle saving this change
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
                delete_unmanaged_channels = guild_config.template_delete_unmanaged
                logger.info(f"  Configuration for deleting unmanaged channels: {delete_unmanaged_channels}")

                if delete_unmanaged_channels:
                    logger.info("  Checking for Discord channels not present in the template...")
                    channels_to_delete = set(live_channels.keys()) - processed_live_channel_ids
                    logger.debug(f"    Found {len(channels_to_delete)} live channel IDs not processed: {channels_to_delete}")
                    
                    for discord_chan_id in channels_to_delete:
                        # Fetch the actual channel object
                        channel_to_delete = discord_guild.get_channel(discord_chan_id)
                        live_chan_data = live_channels.get(discord_chan_id) # Get data for logging
                        chan_name_for_log = live_chan_data['name'] if live_chan_data else f"ID {discord_chan_id}"

                        if channel_to_delete:
                            logger.warning(f"    Discord channel '{chan_name_for_log}' (ID: {discord_chan_id}) is not in the template. Deleting...")
                            try:
                                await channel_to_delete.delete(reason="Removing channel not defined in template")
                                logger.warning(f"      Successfully deleted channel '{chan_name_for_log}'.")
                            except nextcord.Forbidden:
                                logger.error(f"      PERMISSION ERROR: Cannot delete channel '{chan_name_for_log}'.")
                            except nextcord.HTTPException as http_err:
                                logger.error(f"      HTTP ERROR deleting channel '{chan_name_for_log}': {http_err}")
                            except Exception as deletion_err:
                                logger.error(f"      UNEXPECTED ERROR deleting channel '{chan_name_for_log}': {deletion_err}", exc_info=True)
                        else:
                            # This case might happen if a channel was deleted manually during the sync
                            logger.warning(f"    Could not find Discord channel object with ID {discord_chan_id} ('{chan_name_for_log}') to delete. Already deleted?")
                else:
                    logger.debug("  Deletion of unmanaged channels is disabled.")

                # --- Handle Reordering ---
                # TODO: Consider bulk edit for efficiency/accuracy after all CUD operations


                logger.info(f"[apply_template] Channel Create/Update/Delete logic complete. DB updates applied via session commit. Guild: {guild_id}.")

            # Commit changes made to template entities (like discord_channel_id updates)
            # await session.commit() # session_context handles commit/rollback

            # If we reach here without fatal errors, consider it successful
            # TODO: Refine success criteria based on non-fatal errors logged during CUD operations?
            logger.info(f"[apply_template] Successfully applied template changes for guild {guild_id}.")
            return True

        except Exception as e:
            logger.error(f"[apply_template] Error applying template for guild {guild_id}: {e}", exc_info=True)
            # Rollback is handled by session_context
            return False

    async def _apply_category_permissions(self, discord_category: nextcord.CategoryChannel, template_category_id: int, cat_perm_repo: GuildTemplateCategoryPermissionRepository) -> None:
        """Helper to apply permissions stored in the template to a Discord category."""
        logger.debug(f"    Applying permissions for category '{discord_category.name}' (Template ID: {template_category_id})")
        try:
            template_perms = await cat_perm_repo.get_by_category_template_id(template_category_id)
            if not template_perms:
                logger.debug(f"      No specific permissions found in template for category ID {template_category_id}.")
                return

            # Get roles from the guild
            guild_roles = {role.name: role for role in discord_category.guild.roles}

            overwrites = {} # Build the overwrites dictionary
            for perm in template_perms:
                role = guild_roles.get(perm.role_name)
                if not role:
                    logger.warning(f"      Role '{perm.role_name}' defined in template permissions not found on guild '{discord_category.guild.name}'. Skipping permission.")
                    continue

                # Create PermissionOverwrite object
                allow_perms = nextcord.Permissions(perm.allow_permissions_bitfield or 0)
                deny_perms = nextcord.Permissions(perm.deny_permissions_bitfield or 0)
                overwrites[role] = nextcord.PermissionOverwrite.from_pair(allow_perms, deny_perms)
                logger.debug(f"      Prepared overwrite for role '{role.name}': Allow={allow_perms.value}, Deny={deny_perms.value}")

            if overwrites:
                 logger.info(f"    Setting {len(overwrites)} permission overwrites for category '{discord_category.name}'")
                 await discord_category.edit(overwrites=overwrites, reason="Applying template permissions")
                 logger.debug(f"      Successfully applied permissions to category '{discord_category.name}'.")
            else:
                logger.debug(f"      No valid roles found for template permissions on category '{discord_category.name}'. No changes made.")

        except nextcord.Forbidden:
            logger.error(f"      PERMISSION ERROR: Cannot apply permissions to category '{discord_category.name}'. Check bot permissions.")
        except nextcord.HTTPException as http_err:
            logger.error(f"      HTTP ERROR applying permissions to category '{discord_category.name}': {http_err}")
        except Exception as perm_err:
            logger.error(f"      UNEXPECTED ERROR applying permissions to category '{discord_category.name}': {perm_err}", exc_info=True)

    # --- NEW HELPER FUNCTION for Channel Permissions ---
    async def _apply_channel_permissions(
        self, 
        discord_channel: nextcord.abc.GuildChannel, # Use base GuildChannel type
        template_channel_id: int, 
        chan_perm_repo: GuildTemplateChannelPermissionRepository
    ) -> None:
        """Helper to apply permissions stored in the template to a Discord channel."""
        logger.debug(f"    Applying permissions for channel '{discord_channel.name}' (Template ID: {template_channel_id})")
        try:
            template_perms = await chan_perm_repo.get_by_channel_template_id(template_channel_id)
            if not template_perms:
                logger.debug(f"      No specific permissions found in template for channel ID {template_channel_id}.")
                return

            # Get roles from the guild
            guild_roles = {role.name: role for role in discord_channel.guild.roles}

            overwrites = {} # Build the overwrites dictionary
            for perm in template_perms:
                role = guild_roles.get(perm.role_name)
                if not role:
                    logger.warning(f"      Role '{perm.role_name}' defined in template permissions not found on guild '{discord_channel.guild.name}'. Skipping permission.")
                    continue

                # Create PermissionOverwrite object
                # Handle potential None values for bitfields gracefully
                allow_value = perm.allow_permissions_bitfield if perm.allow_permissions_bitfield is not None else 0
                deny_value = perm.deny_permissions_bitfield if perm.deny_permissions_bitfield is not None else 0
                
                allow_perms = nextcord.Permissions(allow_value)
                deny_perms = nextcord.Permissions(deny_value)
                overwrites[role] = nextcord.PermissionOverwrite.from_pair(allow_perms, deny_perms)
                logger.debug(f"      Prepared overwrite for role '{role.name}': Allow={allow_perms.value}, Deny={deny_perms.value}")

            if overwrites:
                 logger.info(f"    Setting {len(overwrites)} permission overwrites for channel '{discord_channel.name}'")
                 await discord_channel.edit(overwrites=overwrites, reason="Applying template permissions")
                 logger.debug(f"      Successfully applied permissions to channel '{discord_channel.name}'.")
            else:
                logger.debug(f"      No valid roles found for template permissions on channel '{discord_channel.name}'. No changes made.")

        except nextcord.Forbidden:
            logger.error(f"      PERMISSION ERROR: Cannot apply permissions to channel '{discord_channel.name}'. Check bot permissions.")
        except nextcord.HTTPException as http_err:
            logger.error(f"      HTTP ERROR applying permissions to channel '{discord_channel.name}': {http_err}")
        except Exception as perm_err:
            logger.error(f"      UNEXPECTED ERROR applying permissions to channel '{discord_channel.name}': {perm_err}", exc_info=True)
    # --- END NEW HELPER FUNCTION ---

    async def sync_guild(self, guild_id: str, sync_members_only: bool = True) -> bool:
        """Synchronize guild data with Discord"""
        logger.info(f"Syncing guild {guild_id} (members_only={sync_members_only})")
        
        try:
            # Get Discord guild
            discord_guild = self.bot.get_guild(int(guild_id))
            if not discord_guild:
                logger.error(f"Could not find Discord guild {guild_id}")
                return False
                
            # Get database guild using the correct repository
            async with session_context() as session:
                # Use GuildRepositoryImpl to get the GuildEntity
                guild_repo = GuildRepositoryImpl(session) 
                db_guild = await guild_repo.get_by_id(guild_id) # Corrected repo and method usage
                
                if not db_guild:
                    # Corrected log message
                    logger.error(f"Could not find GuildEntity {guild_id} in database") 
                    return False
                    
                if not sync_members_only:
                    # Update guild metadata_json using correct attributes
                    db_guild.name = discord_guild.name
                    # Correct attribute access: discord_guild.icon.url (check for None)
                    db_guild.icon_url = str(discord_guild.icon.url) if discord_guild.icon else None 
                    db_guild.member_count = discord_guild.member_count
                    # Ensure owner_id is converted to string
                    db_guild.owner_id = str(discord_guild.owner_id) if discord_guild.owner_id else None 
                    
                    # Save guild updates using the correct repository
                    await guild_repo.update(db_guild)
                    logger.info(f"Updated guild metadata for {guild_id}")
                    
                # Sync members if needed
                if hasattr(self.bot, 'user_workflow'):
                    await self.bot.user_workflow.sync_guild_members(discord_guild)
                else:
                    logger.warning("User workflow not available for member sync")
                    
                return True
            
        except Exception as e:
            logger.error(f"Error syncing guild {guild_id}: {e}")
            return False
            
    async def enforce_access_control(self, guild: GuildEntity) -> None:
        """Enforce access control based on guild status"""
        if guild.access_status in [ACCESS_REJECTED, ACCESS_SUSPENDED]:
            logger.info(f"Enforcing access control for guild {guild.guild_id}")
            try:
                discord_guild = self.bot.get_guild(int(guild.guild_id))
                if discord_guild:
                    await discord_guild.leave()
                    logger.info(f"Left guild {guild.guild_id} due to {guild.access_status} status")
                    
                # Update guild status
                async with session_context() as session:
                    guild_config_repo = GuildConfigRepositoryImpl(session)
                    await guild_config_repo.update(guild)
                    
            except Exception as e:
                logger.error(f"Error enforcing access control for guild {guild.guild_id}: {e}")
                
    def get_guild_status(self, guild_id: str) -> WorkflowStatus:
        """Get the current status of the workflow for a specific guild"""
        return self._guild_statuses.get(guild_id, WorkflowStatus.PENDING)
        
    async def disable_for_guild(self, guild_id: str) -> None:
        """Disable workflow for a specific guild"""
        logger.info(f"Disabling guild workflow for guild {guild_id}")
        self._guild_statuses[guild_id] = WorkflowStatus.DISABLED
        
        # Get guild and update status
        async with session_context() as session:
            guild_config_repo = GuildConfigRepositoryImpl(session)
            guild = await guild_config_repo.get_by_guild_id(guild_id)
            if guild:
                await guild_config_repo.update(guild)
                
    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup resources for a specific guild"""
        logger.info(f"Cleaning up guild workflow for guild {guild_id}")
        if guild_id in self._guild_statuses:
            del self._guild_statuses[guild_id]
            
    async def cleanup(self) -> None:
        """Global cleanup"""
        logger.info("Cleaning up guild workflow")
        self._guild_statuses.clear()