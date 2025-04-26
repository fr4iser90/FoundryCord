import asyncio
import nextcord
from typing import Dict, Optional, List
from datetime import datetime # Import datetime

from app.bot.core.workflows.base_workflow import BaseWorkflow, WorkflowStatus
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.bot.core.workflows.guild_workflow import GuildWorkflow # May need interaction
from app.shared.interface.logging.api import get_bot_logger
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

logger = get_bot_logger()

class GuildTemplateWorkflow(BaseWorkflow):
    """Workflow for creating and managing guild structure templates/snapshots."""

    def __init__(self, database_workflow: DatabaseWorkflow, guild_workflow: GuildWorkflow, bot):
        super().__init__("guild_template") # Give it a unique name
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
        logger.info("Guild Template Workflow initialized.")
        return True

    async def create_template_for_guild(self, guild: nextcord.Guild):
        """Reads the current structure of the guild and saves it as a template."""
        guild_id_str = str(guild.id)
        logger.info(f"Attempting to create structure template for guild: {guild.name} ({guild_id_str})")

        try:
            async with session_context() as session:
                # Instantiate repositories with the current session
                template_repo = GuildTemplateRepositoryImpl(session)
                cat_repo = GuildTemplateCategoryRepositoryImpl(session)
                chan_repo = GuildTemplateChannelRepositoryImpl(session)
                cat_perm_repo = GuildTemplateCategoryPermissionRepositoryImpl(session)
                chan_perm_repo = GuildTemplateChannelPermissionRepositoryImpl(session)

                # 1. Check if a template already exists
                existing_template = await template_repo.get_by_guild_id(guild_id_str)
                if existing_template:
                    logger.info(f"Template already exists for guild {guild_id_str}. Skipping creation.")
                    return True

                # 2. Create the main template record
                template_name = f"Initial Snapshot - {guild.name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
                template_record = await template_repo.create(
                    guild_id=guild_id_str,
                    template_name=template_name
                )
                if not template_record:
                    logger.error(f"Failed to create main template record for guild {guild_id_str}")
                    await session.rollback() # Rollback on failure
                    return False
                template_db_id = template_record.id
                category_template_map = {} # To map Discord category object to template DB ID
                logger.debug(f"Created main template record ID: {template_db_id} for guild {guild_id_str}")

                # --- NEW: Update Guild Config to set this template as active --- 
                update_stmt = (
                    update(GuildConfigEntity)
                    .where(GuildConfigEntity.guild_id == guild_id_str)
                    .values(active_template_id=template_db_id)
                )
                update_result = await session.execute(update_stmt)
                if update_result.rowcount == 0:
                    logger.warning(f"Could not find GuildConfig for guild {guild_id_str} to set initial active template {template_db_id}. Configuration might need creation.")
                    # Decide if this is a critical error. For now, log warning and continue.
                else:
                    logger.info(f"Set initial snapshot template {template_db_id} as active for guild {guild_id_str}")
                # ------------------------------------------------------------

                # --- Initialize Counters ---
                category_count = 0
                channel_count = 0
                cat_perm_count = 0
                chan_perm_count = 0

                # 3. Iterate through categories (sorted by position)
                for category in sorted(guild.categories, key=lambda c: c.position):
                    logger.debug(f"Processing category: {category.name} (Pos: {category.position})")
                    cat_template_record = await cat_repo.create(
                        guild_template_id=template_db_id,
                        category_name=category.name,
                        position=category.position
                    )
                    if not cat_template_record:
                        logger.error(f"Failed to create template category for '{category.name}' in guild {guild_id_str}")
                        await session.rollback()
                        return False
                    category_template_map[category] = cat_template_record.id # Store mapping
                    logger.debug(f"  Created category template record ID: {cat_template_record.id}")
                    category_count += 1 # Increment counter

                    # Save category permissions (overwrites)
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
                                # Continue processing other permissions/channels, maybe log and flag?
                                # For now, let's rollback on any failure for simplicity.
                                await session.rollback()
                                return False
                            logger.debug(f"      Created category permission record ID: {perm_record.id}")
                            cat_perm_count += 1 # Increment counter


                # 4. Iterate through channels (Text, Voice, Stage, Forum - sorted by position)
                # Combine all channel types that have positions and categories/overwrites
                # Note: ForumChannel might behave differently regarding categories/perms. Adjust if needed.
                all_channels = sorted(
                    [ch for ch in guild.channels if isinstance(ch, (nextcord.TextChannel, nextcord.VoiceChannel, nextcord.StageChannel, nextcord.ForumChannel))],
                    key=lambda c: c.position
                )

                for channel in all_channels:
                    logger.debug(f"Processing channel: {channel.name} (Type: {channel.type}, Pos: {channel.position})")
                    parent_template_category_id = category_template_map.get(channel.category) # Get parent template ID if exists
                    logger.debug(f"  Parent category: {channel.category.name if channel.category else 'None'} -> Template ID: {parent_template_category_id}")

                    # Create channel template
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
                         await session.rollback()
                         return False
                    logger.debug(f"  Created channel template record ID: {chan_template_record.id}")
                    channel_count += 1 # Increment counter

                    # Save channel permissions (overwrites)
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
                                await session.rollback()
                                return False
                            logger.debug(f"      Created channel permission record ID: {perm_record.id}")
                            chan_perm_count += 1 # Increment counter

                # 5. Log Summary and Commit
                logger.info(
                    f"Successfully created template for guild {guild.name} ({guild_id_str}) with: "
                    f"{category_count} categories, {channel_count} channels, "
                    f"{cat_perm_count} category permissions, {chan_perm_count} channel permissions."
                )
                # Commit is handled automatically by session_context on successful exit
                return True # Indicate success

        except Exception as e:
            logger.error(f"An error occurred during template creation for guild {guild_id_str}: {e}", exc_info=True)
            # Rollback will happen automatically if session_context exits via exception
            return False # Indicate failure


    async def initialize_for_guild(self, guild_id: str) -> bool:
        """This workflow doesn't need per-guild initialization in the traditional sense."""
        # Mark as active conceptually, as it's ready to be triggered.
        self.guild_status[guild_id] = WorkflowStatus.ACTIVE 
        return True

    async def cleanup(self) -> None:
        logger.info("Cleaning up Guild Template Workflow.")
        await super().cleanup()

    async def cleanup_guild(self, guild_id: str) -> None:
        await super().cleanup_guild(guild_id)
        # No specific per-guild cleanup needed unless we cache things here
