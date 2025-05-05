import logging
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord.entities import GuildEntity, GuildConfigEntity
from app.shared.infrastructure.repositories.discord.guild_repository_impl import GuildRepositoryImpl
from app.shared.infrastructure.repositories.discord.guild_config_repository_impl import GuildConfigRepositoryImpl
from app.bot.application.workflows.base_workflow import WorkflowStatus
import nextcord

logger = get_bot_logger()

# String constants for access status
ACCESS_PENDING = "pending"
ACCESS_APPROVED = "approved"
ACCESS_REJECTED = "rejected"
ACCESS_SUSPENDED = "suspended"

async def approve_guild(self, guild_id: str) -> bool:
    """Approve a guild, update its config, create initial template, and apply it."""
    logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Starting approval process...")
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
                logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Cannot approve: GuildEntity not found in database")
                return False
            
            # 2. Fetch and Update GuildConfig (MUST exist)
            config = await guild_config_repo.get_by_guild_id(guild_id)
            if not config:
                logger.error(f"[GuildWorkflow] [Guild:{guild_id}] CRITICAL FAILURE: GuildConfigEntity not found during approval!")
                return False

            logger.debug(f"[GuildWorkflow] [Guild:{guild_id}] Found existing GuildConfigEntity. Updating features.")
            config_features = { 'dashboard': True, 'tasks': True, 'services': True }
            config.features = config_features
            logger.debug(f"[GuildWorkflow] [Guild:{guild_id}] Updated GuildConfigEntity features (in session).")
            
            self._guild_access_statuses[guild_id] = ACCESS_APPROVED
            self._guild_statuses[guild_id] = WorkflowStatus.PENDING

            # 3. Create Initial Template
            logger.debug(f"[GuildWorkflow] [Guild:{guild_id}] Attempting to fetch nextcord.Guild object...")
            discord_guild = self.bot.get_guild(int(guild_id))
            creation_success = False
            if discord_guild:
                template_workflow = self.bot.workflow_manager.get_workflow("guild_template")
                if template_workflow:
                    logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Triggering template creation...")
                    try:
                        # Pass the session and the config object
                        creation_success = await template_workflow.create_template_for_guild(
                            discord_guild, 
                            guild_config=config, 
                            db_session=session # Use the same session
                        ) 
                        logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Template creation result: {creation_success}")
                    except Exception as template_err:
                        logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Error during template creation call: {template_err}", exc_info=True)
                else:
                    logger.error("[GuildWorkflow] [Guild:{guild_id}] GuildTemplateWorkflow not found!")
            else:
                logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Could not find Discord guild object.")

            # 4. Apply Template (if creation succeeded)
            apply_success = False
            if creation_success:
                logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Attempting to apply template...")
                try:
                    # Pass the current session and the config object (modified in memory by create_template_for_guild)
                    apply_success = await self.apply_template(guild_id, config=config, session=session) 
                except Exception as apply_err:
                    logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Error during apply_template call: {apply_err}", exc_info=True)
                    apply_success = False # Ensure apply_success is False on error
                if apply_success:
                     logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Successfully applied template.")
                        # Update status to ACTIVE only after successful application
                     self._guild_statuses[guild_id] = WorkflowStatus.ACTIVE
                else:
                        logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Failed to apply template. Workflow status remains {self.get_guild_status(guild_id)}.")
            else:
                logger.warning(f"[GuildWorkflow] [Guild:{guild_id}] Skipping template application due to creation failure.")

            # Commit all changes made within this session (status updates, config changes, template creation)
            # session_context handles commit on successful exit, rollback on error
            
            logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Approval process finished. Template Apply Success: {apply_success}. Final Status: {self.get_guild_status(guild_id)}.")
            return True # Return True if approval process finished (regardless of apply success)
            
    except Exception as e:
        guild_id_str = str(guild_id)
        logger.error(f"[GuildWorkflow] [Guild:{guild_id_str}] Error approving guild: {e}", exc_info=True)
        # Ensure status is set to FAILED if not already set or PENDING/ACTIVE
        if guild_id_str not in self._guild_statuses or self._guild_statuses[guild_id_str] not in [WorkflowStatus.ACTIVE, WorkflowStatus.PENDING]:
             self._guild_statuses[guild_id_str] = WorkflowStatus.FAILED
        return False

async def deny_guild(self, guild_id: str) -> bool:
    """Deny a guild"""
    logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Starting denial process...")
    try:
        async with session_context() as session:
            # We need GuildEntity to update access status
            guild_repo = GuildRepositoryImpl(session)
            guild_entity = await guild_repo.get_by_id(guild_id) 
            
            if not guild_entity:
                logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Cannot deny: GuildEntity not found in database")
                return False
            
            # Update access status on GuildEntity
            logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Setting access_status to REJECTED for GuildEntity")
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
            
            logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Denial process finished. Status: REJECTED.")
            return True
            
    except Exception as e:
        logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Error denying guild: {e}", exc_info=True)
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
         logger.error(f"[GuildWorkflow] enforce_access_control called with invalid type: {type(guild_or_config)}")
         return

    if not guild_id or not access_status:
         logger.error(f"[GuildWorkflow] [Guild:{guild_id or 'Unknown'}] Could not determine guild_id or access_status for enforcement: {guild_or_config}")
         return
         
    if access_status in [ACCESS_REJECTED, ACCESS_SUSPENDED]:
        logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Enforcing access control (Status: {access_status})...")
        try:
            discord_guild = self.bot.get_guild(int(guild_id))
            if discord_guild:
                await discord_guild.leave()
                logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Left guild due to {access_status} status")
            else:
                logger.warning(f"[GuildWorkflow] [Guild:{guild_id}] Cannot leave guild for enforcement: Bot is not currently in this guild.")
                
        except nextcord.Forbidden:
             logger.error(f"[GuildWorkflow] [Guild:{guild_id}] PERMISSION ERROR trying to leave guild for enforcement.", exc_info=True)
        except Exception as e:
            logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Error enforcing access control: {e}", exc_info=True)

def get_guild_access_status(self, guild_id: str) -> str:
    """Get the current access status for a guild"""
    return self._guild_access_statuses.get(guild_id, ACCESS_PENDING)

# Placeholder for apply_template - will be imported from template_application.py
# This avoids circular dependencies during the refactoring.
# The actual GuildWorkflow class in __init__.py will assign the real method.
async def _apply_template_placeholder(*args, **kwargs):
    logger.error("Placeholder for apply_template called!")
    return False
