import logging
from app.bot.application.workflows.base_workflow import WorkflowStatus
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.repositories.discord.guild_repository_impl import GuildRepositoryImpl
from app.shared.infrastructure.repositories.discord.guild_config_repository_impl import GuildConfigRepositoryImpl
from .approval import ACCESS_PENDING, ACCESS_APPROVED, ACCESS_REJECTED # Import constants
from nextcord import Guild, CategoryChannel, TextChannel, VoiceChannel, Permissions, Role

logger = get_bot_logger()

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
