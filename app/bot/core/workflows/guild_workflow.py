# app/bot/core/workflows/guild_workflow.py
import logging
from typing import Dict, Optional, List
from app.bot.core.workflows.base_workflow import BaseWorkflow, WorkflowStatus
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord.entities.guild_entity import GuildEntity
from app.shared.infrastructure.models.discord.entities.guild_user_entity import DiscordGuildUserEntity
from app.shared.domain.repositories.discord.guild_config_repository import GuildConfigRepository
from app.shared.infrastructure.repositories.discord.guild_config_repository_impl import GuildConfigRepositoryImpl
from sqlalchemy import select
from datetime import datetime
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.infrastructure.repositories.discord.guild_repository_impl import GuildRepositoryImpl

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
                        logger.info(f"Guild {guild.guild_id} is already APPROVED")
                        
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
                
                # Create default config (but disabled until approved)
                await self.guild_config_repo.create_or_update(
                    guild_id=guild_id,
                    guild_name=discord_guild.name,
                    features={
                        'categories': False,
                        'channels': False,
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
            
            # Get guild from database
            async with session_context() as session:
                guild_config_repo = GuildConfigRepositoryImpl(session)
                guild = await guild_config_repo.get_by_guild_id(guild_id)
                
                if not guild:
                    logger.error(f"Guild {guild_id} not found in database")
                    self._guild_statuses[guild_id] = WorkflowStatus.FAILED
                    return False
                    
                # Store and check access status
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
                
                # Enable features in config
                config = await self.guild_config_repo.get_by_guild_id(guild_id)
                if config:
                    await self.guild_config_repo.create_or_update(
                        guild_id=guild_id,
                        guild_name=guild.name,
                        features={
                            'categories': True,
                            'channels': True,
                            'dashboard': True,
                            'tasks': True,
                            'services': True
                        }
                    )
                
                # Update local status
                self._guild_access_statuses[guild_id] = ACCESS_APPROVED
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
                    guild.is_verified = False
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
                guild.is_verified = False
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