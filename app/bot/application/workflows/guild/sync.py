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
    logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Processing new guild join...")
    try:
        async with session_context() as session:
            guild_repo = GuildRepositoryImpl(session)
            guild_config_repo = GuildConfigRepositoryImpl(session)
            
            discord_guild = self.bot.get_guild(int(guild_id))
            if not discord_guild:
                logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Could not find Discord guild object")
                return False
            
            logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Creating/updating GuildEntity...")
            guild = await guild_repo.create_or_update(
                guild_id=guild_id,
                name=discord_guild.name,
                access_status=ACCESS_PENDING,
                member_count=discord_guild.member_count,
                icon_url=str(discord_guild.icon.url) if discord_guild.icon else None,
                owner_id=str(discord_guild.owner_id) if discord_guild.owner_id else None
            )
            if not guild:
                 logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Failed to create/update GuildEntity.")
                 return False
            logger.info(f"[GuildWorkflow] [Guild:{guild_id}] GuildEntity created/updated successfully.")
            
            logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Attempting to create/update GuildConfigEntity...")
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
                logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Failed to create/update GuildConfigEntity.")
                # This is a significant issue, might warrant returning False
            else:
                logger.info(f"[GuildWorkflow] [Guild:{guild_id}] GuildConfigEntity create/update call completed successfully.")
            
            self._guild_access_statuses[guild_id] = ACCESS_PENDING
            self._guild_statuses[guild_id] = WorkflowStatus.PENDING
            
            logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Finished processing join. Status set to PENDING.")
            return True
    except Exception as e:
        logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Error handling guild join: {e}", exc_info=True) 
        return False

async def initialize_for_guild(self, guild_id: str) -> bool:
    """Initialize workflow for a specific guild"""
    logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Initializing for guild...")
    
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
                logger.error(f"[GuildWorkflow] [Guild:{guild_id}] GuildEntity not found in database")
                self._guild_statuses[guild_id] = WorkflowStatus.FAILED
                return False
                
            # Store and check access status from GuildEntity
            self._guild_access_statuses[guild_id] = guild.access_status
            
            if guild.access_status == ACCESS_REJECTED:
                logger.warning(f"[GuildWorkflow] [Guild:{guild_id}] Guild is REJECTED access")
                self._guild_statuses[guild_id] = WorkflowStatus.UNAUTHORIZED
                await self.enforce_access_control(guild)
                return False
                
            if guild.access_status != ACCESS_APPROVED:
                logger.warning(f"[GuildWorkflow] [Guild:{guild_id}] Guild is PENDING approval")
                self._guild_statuses[guild_id] = WorkflowStatus.PENDING
                return False
                
            # Perform full guild sync for approved guilds
            logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Guild is APPROVED, performing full sync")
            success = await self.sync_guild(guild_id, sync_members_only=False)
            if not success:
                self._guild_statuses[guild_id] = WorkflowStatus.FAILED
                return False
                
            # Mark as active if everything succeeded
            self._guild_statuses[guild_id] = WorkflowStatus.ACTIVE
            logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Initialization successful. Status: ACTIVE")
            return True
        
    except Exception as e:
        logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Error initializing: {e}", exc_info=True)
        self._guild_statuses[guild_id] = WorkflowStatus.FAILED
        return False

async def sync_guild(self, guild_id: str, sync_members_only: bool = True) -> bool:
    """Synchronize guild data with Discord"""
    logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Starting sync (members_only={sync_members_only})...")
    try:
        discord_guild = self.bot.get_guild(int(guild_id))
        if not discord_guild:
            logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Could not find Discord guild object")
            return False
            
        async with session_context() as session:
            guild_repo = GuildRepositoryImpl(session) 
            db_guild = await guild_repo.get_by_id(guild_id)
            if not db_guild:
                logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Could not find GuildEntity in database") 
                return False
                
            if not sync_members_only:
                db_guild.name = discord_guild.name
                db_guild.icon_url = str(discord_guild.icon.url) if discord_guild.icon else None 
                db_guild.member_count = discord_guild.member_count
                db_guild.owner_id = str(discord_guild.owner_id) if discord_guild.owner_id else None 
                await guild_repo.update(db_guild) # Use update for existing entity
                logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Updated guild metadata.")
                
            # Sync members if user_workflow exists
            user_workflow = self.bot.workflow_manager.get_workflow("user")
            if user_workflow:
                logger.debug(f"[GuildWorkflow] [Guild:{guild_id}] Calling UserWorkflow.sync_guild_members...")
                await user_workflow.sync_guild_members(discord_guild)
                logger.debug(f"[GuildWorkflow] [Guild:{guild_id}] UserWorkflow.sync_guild_members finished.")
            else:
                logger.warning(f"[GuildWorkflow] [Guild:{guild_id}] User workflow not available for member sync")
            logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Sync successful (members_only={sync_members_only}).")
            return True
    except Exception as e:
        logger.error(f"[GuildWorkflow] [Guild:{guild_id}] Error syncing guild: {e}", exc_info=True)
        return False
