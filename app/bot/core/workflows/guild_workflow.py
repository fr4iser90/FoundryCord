# app/bot/core/workflows/guild_workflow.py
import logging
from typing import Dict, Optional, List
from app.bot.core.workflows.base_workflow import BaseWorkflow, WorkflowStatus
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord import GuildEntity
from app.shared.infrastructure.models.discord import DiscordGuildUserEntity
from app.shared.domain.repositories.discord import GuildConfigRepository
from app.shared.infrastructure.repositories.discord import GuildConfigRepositoryImpl
from app.shared.domain.models.discord.guild_model import GuildAccessStatus
from sqlalchemy import select
from datetime import datetime
from app.bot.core.workflows.database_workflow import DatabaseWorkflow

logger = get_bot_logger()

class GuildWorkflow(BaseWorkflow):
    """Manages guild-related operations and synchronization"""
    
    def __init__(self, database_workflow: DatabaseWorkflow, bot):
        super().__init__("guild")
        self.bot = bot
        self.database_workflow = database_workflow
        self.requires_guild_approval = True
        self._guild_statuses: Dict[str, WorkflowStatus] = {}
        self._guild_access_statuses: Dict[str, GuildAccessStatus] = {}
        
        # Add database dependency
        self.add_dependency("database")
        
    async def initialize(self) -> bool:
        """Global initialization - minimal setup for all guilds"""
        logger.info("Initializing guild workflow")
        try:
            # Basic setup and validation
            async with session_context() as session:
                guild_config_repo = GuildConfigRepositoryImpl(session)
                guilds = await guild_config_repo.get_all()
                for guild in guilds:
                    # Store both workflow status and access status
                    access_status = GuildAccessStatus(guild.access_status)
                    self._guild_access_statuses[guild.guild_id] = access_status
                    
                    # Set workflow status based on access status
                    # All guilds start as PENDING unless explicitly approved
                    if access_status == GuildAccessStatus.APPROVED:
                        self._guild_statuses[guild.guild_id] = WorkflowStatus.ACTIVE
                        logger.info(f"Guild {guild.guild_id} is APPROVED")
                    elif access_status == GuildAccessStatus.DENIED:
                        self._guild_statuses[guild.guild_id] = WorkflowStatus.UNAUTHORIZED
                        logger.info(f"Guild {guild.guild_id} is DENIED")
                    else:
                        # Default to PENDING for any other status
                        self._guild_statuses[guild.guild_id] = WorkflowStatus.PENDING
                        guild.access_status = GuildAccessStatus.PENDING.value
                        await guild_config_repo.update(guild)
                        logger.info(f"Guild {guild.guild_id} is PENDING approval")
                    
            return True
        except Exception as e:
            logger.error(f"Error in guild workflow initialization: {e}")
            return False
            
    async def initialize_for_guild(self, guild_id: str) -> bool:
        """Initialize workflow for a specific guild"""
        logger.info(f"Initializing guild workflow for guild {guild_id}")
        
        try:
            # Update status to initializing
            self._guild_statuses[guild_id] = WorkflowStatus.INITIALIZING
            
            # Get guild from database
            async with session_context() as session:
                guild_config_repo = GuildConfigRepositoryImpl(session)
                guild = await guild_config_repo.get_by_guild_id(guild_id)
                
                if not guild:
                    logger.error(f"Guild {guild_id} not found in database")
                    self._guild_statuses[guild_id] = WorkflowStatus.FAILED
                    return False
                    
                # Store and check access status
                access_status = GuildAccessStatus(guild.access_status)
                self._guild_access_statuses[guild_id] = access_status
                
                if access_status == GuildAccessStatus.DENIED:
                    logger.warning(f"Guild {guild_id} is DENIED access")
                    self._guild_statuses[guild_id] = WorkflowStatus.UNAUTHORIZED
                    await self.enforce_access_control(guild)
                    return False
                    
                if access_status != GuildAccessStatus.APPROVED:
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

    def get_guild_access_status(self, guild_id: str) -> GuildAccessStatus:
        """Get the current access status for a guild"""
        return self._guild_access_statuses.get(guild_id, GuildAccessStatus.PENDING)

    async def approve_guild(self, guild_id: str) -> bool:
        """Approve a guild"""
        try:
            async with session_context() as session:
                guild_config_repo = GuildConfigRepositoryImpl(session)
                guild = await guild_config_repo.get_by_guild_id(guild_id)
                
                if not guild:
                    logger.error(f"Cannot approve guild {guild_id}: not found in database")
                    return False
                
                # Update access status
                guild.access_status = GuildAccessStatus.APPROVED.value
                await guild_config_repo.update(guild)
                
                # Update local status
                self._guild_access_statuses[guild_id] = GuildAccessStatus.APPROVED
                self._guild_statuses[guild_id] = WorkflowStatus.PENDING
                
                # Re-initialize the guild
                await self.initialize_for_guild(guild_id)
                
                logger.info(f"Guild {guild_id} has been APPROVED")
                return True
                
        except Exception as e:
            logger.error(f"Error approving guild {guild_id}: {e}")
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
                guild.access_status = GuildAccessStatus.DENIED.value
                await guild_config_repo.update(guild)
                
                # Update local status
                self._guild_access_statuses[guild_id] = GuildAccessStatus.DENIED
                self._guild_statuses[guild_id] = WorkflowStatus.UNAUTHORIZED
                
                # Enforce access control
                await self.enforce_access_control(guild)
                
                logger.info(f"Guild {guild_id} has been DENIED")
                return True
                
        except Exception as e:
            logger.error(f"Error denying guild {guild_id}: {e}")
            return False

    async def sync_guild(self, guild_id: str, sync_members_only: bool = True) -> bool:
        """Synchronize guild data with Discord"""
        logger.info(f"Syncing guild {guild_id} (members_only={sync_members_only})")
        
        try:
            # Get Discord guild
            discord_guild = self.bot.get_guild(int(guild_id))
            if not discord_guild:
                logger.error(f"Could not find Discord guild {guild_id}")
                return False
                
            # Get database guild
            async with session_context() as session:
                guild_config_repo = GuildConfigRepositoryImpl(session)
                db_guild = await guild_config_repo.get_by_guild_id(guild_id)
                if not db_guild:
                    logger.error(f"Could not find database guild {guild_id}")
                    return False
                    
                if not sync_members_only:
                    # Update guild metadata
                    db_guild.name = discord_guild.name
                    db_guild.icon_url = str(discord_guild.icon_url) if discord_guild.icon_url else None
                    db_guild.member_count = discord_guild.member_count
                    db_guild.owner_id = str(discord_guild.owner_id)
                    
                    # Save guild updates
                    await guild_config_repo.update(db_guild)
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
        if guild.access_status in [GuildAccessStatus.DENIED.value, GuildAccessStatus.BLOCKED.value]:
            logger.info(f"Enforcing access control for guild {guild.guild_id}")
            try:
                discord_guild = self.bot.get_guild(int(guild.guild_id))
                if discord_guild:
                    await discord_guild.leave()
                    logger.info(f"Left guild {guild.guild_id} due to {guild.access_status} status")
                    
                # Update guild status
                async with session_context() as session:
                    guild_config_repo = GuildConfigRepositoryImpl(session)
                    guild.is_active = False
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
                guild.is_active = False
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