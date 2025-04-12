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
                logger.debug(f"Attempting to fetch discord.Guild object for ID: {guild_id}")
                discord_guild = self.bot.get_guild(int(guild_id))
                
                if discord_guild:
                    logger.debug(f"Found discord.Guild object: {discord_guild.name}")
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
                cat_repo = GuildTemplateCategoryRepositoryImpl(session)
                chan_repo = GuildTemplateChannelRepositoryImpl(session)
                cat_perm_repo = GuildTemplateCategoryPermissionRepositoryImpl(session)
                chan_perm_repo = GuildTemplateChannelPermissionRepositoryImpl(session)

                # 1. Load Template Data
                template = await template_repo.get_by_guild_id(guild_id)
                if not template:
                    logger.warning(f"[apply_template] No template found for guild {guild_id}. Cannot apply.")
                    return False # Or True?

                template_categories = await cat_repo.get_by_template_id(template.id)
                template_channels = await chan_repo.get_by_template_id(template.id)
                # TODO: Load permissions

                logger.info(f"[apply_template] Loaded template '{template.template_name}' for guild {guild_id}")
                logger.debug(f"  Template contains {len(template_categories)} categories and {len(template_channels)} channels.")

                # ----------------------------------------------------------
                # 2. Get Current Discord State
                # ----------------------------------------------------------
                discord_categories_list = discord_guild.categories
                discord_channels_list = discord_guild.channels # All channels

                # --- Create Lookups for easy access ---
                # Map template category name -> template category object
                template_categories_by_name = {cat.category_name: cat for cat in template_categories}
                # Map Discord category name -> Discord category object
                discord_categories_by_name = {cat.name: cat for cat in discord_categories_list}

                logger.debug(f"  Found {len(discord_categories_list)} categories currently on Discord.")

                # ----------------------------------------------------------
                # 3. Process Categories (Create/Update on Discord based on Template)
                # ----------------------------------------------------------
                created_discord_categories = {} # Map template cat ID -> created/found discord cat object

                # Sort template categories by position for correct creation order
                sorted_template_categories = sorted(template_categories, key=lambda c: c.position)

                for template_cat in sorted_template_categories:
                    logger.debug(f"  Processing template category: '{template_cat.category_name}' (Pos: {template_cat.position})")
                    existing_discord_cat = discord_categories_by_name.get(template_cat.category_name)

                    if existing_discord_cat:
                        logger.info(f"    Category '{template_cat.category_name}' already exists on Discord.")
                        # TODO: Update position? Apply permissions?
                        # For now, just record the mapping
                        created_discord_categories[template_cat.id] = existing_discord_cat
                        # Apply permissions (placeholder)
                        await self._apply_category_permissions(existing_discord_cat, template_cat.id, cat_perm_repo)

                    else:
                        logger.info(f"    Category '{template_cat.category_name}' does not exist. Creating...")
                        try:
                            # Basic creation with name
                            # TODO: Apply overwrites/permissions during creation if possible?
                            new_discord_cat = await discord_guild.create_category(
                                name=template_cat.category_name,
                                reason=f"Applying template: {template.template_name}"
                            )
                            logger.info(f"      Successfully created category '{new_discord_cat.name}' (ID: {new_discord_cat.id})")
                            created_discord_categories[template_cat.id] = new_discord_cat

                            # TODO: Set position AFTER creation if needed (might require separate call)
                            # await new_discord_cat.edit(position=template_cat.position)

                            # Apply permissions after creation
                            await self._apply_category_permissions(new_discord_cat, template_cat.id, cat_perm_repo)

                        except nextcord.Forbidden:
                            logger.error(f"      PERMISSION ERROR: Cannot create category '{template_cat.category_name}'. Check bot permissions.")
                            # Decide how to handle: continue? rollback? stop?
                            # For now, let's log and continue, but this might leave state inconsistent.
                        except nextcord.HTTPException as http_err:
                            logger.error(f"      HTTP ERROR creating category '{template_cat.category_name}': {http_err}")
                        except Exception as creation_err:
                             logger.error(f"      UNEXPECTED ERROR creating category '{template_cat.category_name}': {creation_err}", exc_info=True)

                # ----------------------------------------------------------
                # 4. Process Categories (Delete from Discord if not in Template - Optional)
                # ----------------------------------------------------------
                # TODO: Make deletion configurable
                delete_unmanaged = False # Set to True to enable deletion
                if delete_unmanaged:
                    logger.info("  Checking for Discord categories not present in the template...")
                    for discord_cat_name, discord_cat in discord_categories_by_name.items():
                        if discord_cat_name not in template_categories_by_name:
                            logger.warning(f"    Discord category '{discord_cat_name}' is not in the template. Deleting...")
                            try:
                                await discord_cat.delete(reason="Removing category not defined in template")
                                logger.warning(f"      Successfully deleted category '{discord_cat_name}'.")
                            except nextcord.Forbidden:
                                logger.error(f"      PERMISSION ERROR: Cannot delete category '{discord_cat_name}'.")
                            except nextcord.HTTPException as http_err:
                                logger.error(f"      HTTP ERROR deleting category '{discord_cat_name}': {http_err}")
                            except Exception as deletion_err:
                                logger.error(f"      UNEXPECTED ERROR deleting category '{discord_cat_name}': {deletion_err}", exc_info=True)
                else:
                    logger.debug("  Deletion of unmanaged categories is disabled.")

                # ----------------------------------------------------------
                # 5. Process Channels (Create/Update/Delete)
                # ----------------------------------------------------------
                # TODO: Similar logic as categories, but associate with correct created_discord_categories[parent_id]
                # TODO: **Crucially: Update template_channels.discord_channel_id in the database**
                logger.warning(f"[apply_template] Channel processing logic for guild {guild_id} is not yet implemented.")

            # If we reach here without errors (even if logic is missing), assume success for now
            logger.info(f"[apply_template] Category processing (partially) completed for guild {guild_id}. Returning True.")
            return True

        except Exception as e:
            logger.error(f"[apply_template] Error applying template for guild {guild_id}: {e}", exc_info=True)
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