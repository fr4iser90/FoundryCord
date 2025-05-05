import asyncio
import nextcord
from nextcord import Interaction
from typing import Dict, Optional, List
from datetime import datetime # Import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.application.workflows.base_workflow import BaseWorkflow, WorkflowStatus
from app.bot.application.workflows.database_workflow import DatabaseWorkflow
from app.bot.application.workflows.guild import GuildWorkflow # May need interaction
from app.shared.interfaces.logging.api import get_bot_logger
from app.shared.infrastructure.database.session.context import session_context
# --- Import Repository Implementations ---
from app.shared.infrastructure.repositories.guild_templates import (
    GuildTemplateRepositoryImpl,
    GuildTemplateCategoryRepositoryImpl,
    GuildTemplateChannelRepositoryImpl,
    GuildTemplateCategoryPermissionRepositoryImpl,
    GuildTemplateChannelPermissionRepositoryImpl
)
# --- Import Domain Interfaces (Optional but good practice for type hints) ---
from app.shared.domain.repositories.guild_templates import (
    GuildTemplateRepository,
    GuildTemplateCategoryRepository,
    GuildTemplateChannelRepository,
    GuildTemplateCategoryPermissionRepository,
    GuildTemplateChannelPermissionRepository
)
from app.shared.infrastructure.models.discord.entities import GuildConfigEntity
from sqlalchemy import select, update
# --- ADD GuildConfig Repo Import ---
# from app.shared.infrastructure.repositories.discord.guild_config_repository_impl import GuildConfigRepositoryImpl
# ----------------------------------

logger = get_bot_logger()

class GuildTemplateWorkflow(BaseWorkflow):
    """Workflow for creating and managing guild structure templates/snapshots."""

    def __init__(self, database_workflow: DatabaseWorkflow, guild_workflow: GuildWorkflow, bot):
        super().__init__("guild_template")
        self.database_workflow = database_workflow
        self.guild_workflow = guild_workflow
        self.bot = bot
        # Define dependencies
        self.add_dependency("database")
        self.add_dependency("guild") # Depends on basic guild info being available

        # This workflow itself might not need per-guild init,
        # but its actions are triggered per-guild.
        self.requires_guild_approval = False # It reads structure *after* approval
        self.auto_initialize = False # Doesn't auto-init per guild, triggered explicitly

        # Repositories will be instantiated per-operation using session_context
        self.guild_template_repo: Optional[GuildTemplateRepository] = None
        self.guild_template_category_repo: Optional[GuildTemplateCategoryRepository] = None
        self.guild_template_channel_repo: Optional[GuildTemplateChannelRepository] = None
        self.guild_template_category_perm_repo: Optional[GuildTemplateCategoryPermissionRepository] = None
        self.guild_template_channel_perm_repo: Optional[GuildTemplateChannelPermissionRepository] = None


    async def initialize(self) -> bool:
        """Initialize the workflow globally."""
        # Repositories are session-scoped, so no global initialization needed here.
        logger.debug("[GuildTemplateWorkflow] Initialized successfully.")
        return True

    async def create_template_for_guild(self, 
                                      guild: nextcord.Guild, 
                                      guild_config: GuildConfigEntity, # Mandatory guild config object
                                      db_session: Optional[AsyncSession] = None):
        """Reads the current structure of the guild and saves it as a template.
        
        Args:
            guild: The nextcord Guild object.
            guild_config: The existing GuildConfigEntity object for this guild.
            db_session: An optional existing SQLAlchemy AsyncSession to use. 
                        If None, a new session context will be created.
        """
        guild_id_str = str(guild.id)
        logger.info(f"[GuildTemplateWorkflow] [Guild:{guild_id_str}] Starting template creation for guild '{guild.name}'...")

        # Determine if we need to create a session context or use the provided one
        if db_session:
            return await self._create_template_with_session(guild, guild_id_str, guild_config, db_session)
        else:
            try:
                async with session_context() as session:
                    return await self._create_template_with_session(guild, guild_id_str, guild_config, session)
            except Exception as e:
                logger.error(f"[GuildTemplateWorkflow] [Guild:{guild_id_str}] Error during template creation (outer scope): {e}", exc_info=True)
                return False

    async def _create_template_with_session(self, 
                                            guild: nextcord.Guild, 
                                            guild_id_str: str, 
                                            guild_config: GuildConfigEntity, # Use passed object
                                            session: AsyncSession) -> bool:
        """Core logic for template creation, requires an active session and the guild config object."""
        try:
            template_repo = GuildTemplateRepositoryImpl(session)
            cat_repo = GuildTemplateCategoryRepositoryImpl(session)
            chan_repo = GuildTemplateChannelRepositoryImpl(session)
            cat_perm_repo = GuildTemplateCategoryPermissionRepositoryImpl(session)
            chan_perm_repo = GuildTemplateChannelPermissionRepositoryImpl(session)
            # GuildConfig Repo is no longer instantiated here; the object is passed in

            existing_template = await template_repo.get_by_guild_id(guild_id_str)
            if existing_template:
                logger.info(f"[GuildTemplateWorkflow] [Guild:{guild_id_str}] Template already exists for guild. Checking active status.")
                template_db_id = existing_template.id
                logger.debug(f"[GuildTemplateWorkflow] [Guild:{guild_id_str}] Existing template found ID: {template_db_id}")
            else:
                template_name = f"Initial Snapshot - {guild.name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
                template_record = await template_repo.create(
                    guild_id=guild_id_str,
                    template_name=template_name
                )
                if not template_record:
                    logger.error(f"Failed to create main template record for guild {guild_id_str}")
                    return False
                template_db_id = template_record.id
                logger.debug(f"[GuildTemplateWorkflow] [Guild:{guild_id_str}] Created main template record ID: {template_db_id}")
            
            # --- Update GuildConfig ---
            try:
                # Directly use the passed guild_config object
                if guild_config.active_template_id != template_db_id:
                    logger.info(f"[GuildTemplateWorkflow] [Guild:{guild_id_str}] Setting active_template_id to {template_db_id} on passed GuildConfig object")
                    guild_config.active_template_id = template_db_id
                    # The change to guild_config will be committed by the caller (GuildWorkflow)
                    logger.info(f"[GuildTemplateWorkflow] [Guild:{guild_id_str}] Successfully set active_template_id on GuildConfig object.")
                else:
                    logger.info(f"[GuildTemplateWorkflow] [Guild:{guild_id_str}] Template {template_db_id} is already active on passed GuildConfig object. No change needed.")
                
            except AttributeError as attr_err:
                logger.error(f"[GuildTemplateWorkflow] [Guild:{guild_id_str}] AttributeError working with passed GuildConfig object: {attr_err}", exc_info=True)
                return False # Critical error
            except Exception as config_err:
                 logger.error(f"[GuildTemplateWorkflow] [Guild:{guild_id_str}] Error updating passed GuildConfig object: {config_err}", exc_info=True)
                 return False # Critical error
            # --- End Update GuildConfig ---

            if existing_template:
                # If the template already existed, we only needed to ensure it's set as active.
                # We don't need to re-process the guild structure.
                logger.debug("[GuildTemplateWorkflow] Skipping structure processing as template already existed.")
                return True

            # --- Process Guild Structure --- 
            category_template_map = {} # Map: nextcord.CategoryChannel -> template_category.id
            category_count = 0
            channel_count = 0
            cat_perm_count = 0
            chan_perm_count = 0

            for category in sorted(guild.categories, key=lambda c: c.position):
                 logger.debug(f"Processing category: {category.name} (Pos: {category.position})")
                 cat_template_record = await cat_repo.create(
                     guild_template_id=template_db_id,
                     category_name=category.name,
                     position=category.position
                 )
                 if not cat_template_record:
                     logger.error(f"Failed to create template category for '{category.name}' in guild {guild_id_str}")
                     return False 
                 category_template_map[category] = cat_template_record.id 
                 logger.debug(f"  Created category template record ID: {cat_template_record.id}")
                 category_count += 1
                 # Process permissions for the category
                 for target, overwrite in category.overwrites.items():
                     if isinstance(target, nextcord.Role):
                         logger.debug(f"    Processing category permission for role: {target.name}")
                         allow_perms, deny_perms = overwrite.pair()
                         perm_record = await cat_perm_repo.create(
                             category_template_id=cat_template_record.id,
                             role_name=target.name,
                             allow_permissions_bitfield=allow_perms.value if allow_perms.value != 0 else None,
                             deny_permissions_bitfield=deny_perms.value if deny_perms.value != 0 else None
                         )
                         if not perm_record:
                             logger.error(f"    Failed to create category permission for role '{target.name}' in category '{category.name}'")
                             return False 
                         logger.debug(f"      Created category permission record ID: {perm_record.id}")
                         cat_perm_count += 1

            # Process channels (including those without categories)
            all_channels = sorted(
                 [ch for ch in guild.channels if isinstance(ch, (nextcord.TextChannel, nextcord.VoiceChannel, nextcord.StageChannel, nextcord.ForumChannel))],
                 key=lambda c: c.position # Keep debug logs concise for now, prefix optional
             )
            for channel in all_channels:
                 logger.debug(f"Processing channel: {channel.name} (Type: {channel.type}, Pos: {channel.position})")
                 parent_template_category_id = category_template_map.get(channel.category) # Returns None if channel.category is None or not in map
                 logger.debug(f"  Parent category: {channel.category.name if channel.category else 'None'} -> Template ID: {parent_template_category_id}")
 
                 chan_template_record = await chan_repo.create(
                     guild_template_id=template_db_id,
                     channel_name=channel.name,
                     channel_type=str(channel.type),
                     position=channel.position,
                     topic=getattr(channel, 'topic', None),
                     is_nsfw=getattr(channel, 'nsfw', False),
                     slowmode_delay=getattr(channel, 'slowmode_delay', 0) if isinstance(channel, nextcord.TextChannel) else 0,
                     parent_category_template_id=parent_template_category_id
                 )
                 if not chan_template_record:
                      logger.error(f"Failed to create template channel for '{channel.name}' in guild {guild_id_str}")
                      return False 
                 logger.debug(f"  Created channel template record ID: {chan_template_record.id}")
                 channel_count += 1 
                 # Process permissions for the channel
                 for target, overwrite in channel.overwrites.items():
                     if isinstance(target, nextcord.Role):
                         logger.debug(f"    Processing channel permission for role: {target.name}")
                         allow_perms, deny_perms = overwrite.pair()
                         perm_record = await chan_perm_repo.create(
                             channel_template_id=chan_template_record.id,
                             role_name=target.name,
                             allow_permissions_bitfield=allow_perms.value if allow_perms.value != 0 else None,
                             deny_permissions_bitfield=deny_perms.value if deny_perms.value != 0 else None
                         )
                         if not perm_record:
                             logger.error(f"    Failed to create channel permission for role '{target.name}' in channel '{channel.name}'")
                             return False 
                         logger.debug(f"      Created channel permission record ID: {perm_record.id}")
                         chan_perm_count += 1
            logger.info(
                f"[GuildTemplateWorkflow] [Guild:{guild_id_str}] Template creation successful: "
                f"{category_count} categories, {channel_count} channels, "
                f"{cat_perm_count} category permissions, {chan_perm_count} channel permissions."
            )
            return True

        except Exception as e:
            logger.error(f"[GuildTemplateWorkflow] [Guild:{guild_id_str}] Error during template creation (inner scope): {e}", exc_info=True)
            # Rollback is handled by the session_context manager
            return False


    async def initialize_for_guild(self, guild_id: str) -> bool:
        """This workflow doesn't need per-guild initialization in the traditional sense."""
        # Mark as active conceptually, as it's ready to be triggered when needed.
        self.guild_status[guild_id] = WorkflowStatus.ACTIVE 
        return True

    async def cleanup(self) -> None:
        logger.info("[GuildTemplateWorkflow] Cleanup successful.")
        await super().cleanup()

    async def cleanup_guild(self, guild_id: str) -> None:
        await super().cleanup_guild(guild_id)
        # No specific per-guild cleanup needed unless we cache things here
