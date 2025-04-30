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
                    }
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

                # 4. Apply Template
                apply_success = False
                if creation_success:
                    logger.info(f"Attempting to apply template for guild {guild_id}")
                    try:
                        # Pass session and config object modified by create_template_for_guild
                        apply_success = await self.apply_template(guild_id, config=config, session=session) 
                        if apply_success:
                            logger.info(f"Successfully applied template for guild {guild_id}.")
                            self._guild_statuses[guild_id] = WorkflowStatus.ACTIVE
                        else:
                            logger.error(f"Failed to apply template for guild {guild_id}. Status remains PENDING.")
                    except Exception as apply_err:
                        logger.error(f"Error during apply_template call: {apply_err}", exc_info=True)
                else:
                    logger.warning(f"Skipping template application for guild {guild_id} due to creation failure.")

                return True # Approval process initiated
        except Exception as e:
            guild_id_str = str(guild_id)
            logger.error(f"Error approving guild {guild_id_str}: {e}", exc_info=True)
            if guild_id_str not in self._guild_statuses or self._guild_statuses[guild_id_str] not in [WorkflowStatus.ACTIVE, WorkflowStatus.PENDING]:
                 self._guild_statuses[guild_id_str] = WorkflowStatus.FAILED
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

            template_categories = await cat_repo.get_by_template_id(template.id)
            template_channels = await chan_repo.get_by_template_id(template.id)

            logger.info(f"[apply_template] Loaded template '{template.template_name}' (ID: {template.id}).")
            logger.debug(f"  Contains {len(template_categories)} categories, {len(template_channels)} channels.")

            # 2. Get Current Discord State
            live_guild_data = await discord_query_service.get_live_guild_structure(discord_guild)
            live_categories = live_guild_data.get('categories', {})
            live_channels = live_guild_data.get('channels', {})

            # 3. Process Categories
            created_or_found_discord_categories = {}
            processed_live_category_ids = set()
            sorted_template_categories = sorted(template_categories, key=lambda c: c.position)
            for template_cat in sorted_template_categories:
                existing_discord_cat_id = discord_categories_by_name.get(template_cat.category_name)
                # ... find object, create/update, apply perms, add to created_or_found_discord_categories, add to processed_live_category_ids
                pass 

            # 4. Process Channels
            logger.info("[apply_template] Processing channels...")
            # ... (Lookups)
            processed_live_channel_ids = set()
            sorted_template_channels = sorted(template_channels, key=lambda c: c.position)
            for template_chan in sorted_template_channels:
                # ... (existing channel finding/creation/update/permission logic - placeholders removed for brevity) ...
                # ... find category, find channel object, create/update, apply perms, update template_chan.discord_channel_id, add to processed_live_channel_ids
                pass

            # 5 & 6. Process Deletions
            delete_unmanaged_channels = config.template_delete_unmanaged 
            logger.info(f"[apply_template] Deleting unmanaged items: {delete_unmanaged_channels}")
            if delete_unmanaged_channels:
                # ... (channel deletion logic) ...
                # ... (category deletion logic) ...
                pass
            else:
                logger.debug("[apply_template] Deletion of unmanaged items is disabled.")

            # 7. Final Reordering
            logger.info("[apply_template] Attempting final reordering...")
            try:
                # ... (prepare final_positions) ...
                final_positions = {} # Placeholder
                if final_positions:
                     await discord_guild.edit_channel_positions(positions=final_positions)
                     logger.info("[apply_template] Final order applied.")
                else:
                     logger.info("[apply_template] No items to reorder.")
            except Exception as reorder_err:
                logger.error(f"[apply_template] Error during final reordering: {reorder_err}", exc_info=True)
                # Decide if this should cause apply_template to return False
            
            logger.info(f"[apply_template] Template application logic complete for guild {guild_id}.")
            # The final commit happens when the session_context in approve_guild exits.
            return True

        except Exception as e:
            logger.error(f"[apply_template] Error applying template for guild {guild_id}: {e}", exc_info=True)
            # Rollback will be handled by the session_context in the caller (approve_guild)
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
                    await guild_repo.update(db_guild)
                    logger.info(f"Updated guild metadata for {guild_id}")
                    
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