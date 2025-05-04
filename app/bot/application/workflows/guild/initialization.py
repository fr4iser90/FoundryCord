import logging
from typing import Dict
from app.bot.application.workflows.base_workflow import WorkflowStatus
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.repositories.discord.guild_repository_impl import GuildRepositoryImpl
from app.shared.infrastructure.repositories.discord.guild_config_repository_impl import GuildConfigRepositoryImpl
from .approval import ACCESS_PENDING, ACCESS_APPROVED, ACCESS_REJECTED, ACCESS_SUSPENDED # Import constants

logger = get_bot_logger()

async def initialize(self) -> bool:
    """Global initialization - minimal setup for all guilds"""
    logger.info("[Initialize] Initializing guild workflow")
    try:
        async with session_context() as session:
            guild_repo = GuildRepositoryImpl(session)
            guild_config_repo = GuildConfigRepositoryImpl(session)
            
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
