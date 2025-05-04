from typing import List
import logging
from nextcord import Guild, Member
from app.shared.infrastructure.models.discord.entities.guild_user_entity import DiscordGuildUserEntity
from app.shared.domain.repositories.auth.user_repository import UserRepository
from .base_workflow import BaseWorkflow, WorkflowStatus
from app.shared.interface.logging.api import get_bot_logger
from sqlalchemy import select
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.repositories.auth.user_repository_impl import UserRepositoryImpl

logger = get_bot_logger()

class UserWorkflow(BaseWorkflow):
    """Workflow for managing Discord users"""
    
    def __init__(self, database_workflow, bot=None):
        super().__init__("user")
        self.database_workflow = database_workflow
        self.bot = bot
        
        # Add dependencies
        self.add_dependency("database")
        
        # This workflow doesn't require guild approval to sync members
        self.requires_guild_approval = False
    
    async def initialize(self) -> bool:
        """Initialize the user workflow globally"""
        logger.info("Initializing user workflow")
        
        try:
            # Mark all guilds as pending initially
            if hasattr(self, 'bot') and self.bot:
                for guild in self.bot.guilds:
                    self.guild_status[str(guild.id)] = WorkflowStatus.PENDING
                    # Sync users immediately for all guilds
                    await self.sync_guild_members(guild)
            
            logger.info("User workflow initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize user workflow: {str(e)}")
            return False

    async def initialize_for_guild(self, guild_id: str) -> bool:
        """Initialize workflow for a specific guild"""
        try:
            # Update status to initializing
            self.guild_status[guild_id] = WorkflowStatus.INITIALIZING
            
            # Get the guild
            if not self.bot:
                logger.error("Bot instance not available")
                self.guild_status[guild_id] = WorkflowStatus.FAILED
                return False
                
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id}")
                self.guild_status[guild_id] = WorkflowStatus.FAILED
                return False
            
            # Sync guild members regardless of approval status
            await self.sync_guild_members(guild)
            
            # Mark as active
            self.guild_status[guild_id] = WorkflowStatus.ACTIVE
            return True
            
        except Exception as e:
            logger.error(f"Error initializing user workflow for guild {guild_id}: {e}")
            self.guild_status[guild_id] = WorkflowStatus.FAILED
            return False

    async def sync_guild_to_database(self, guild):
        """Synchronize guild data to database"""
        try:
            from app.shared.infrastructure.models.discord import GuildEntity
            
            async with session_context() as session:
                # Check if guild exists
                result = await session.execute(
                    select(GuildEntity).where(GuildEntity.guild_id == str(guild.id))
                )
                guild_entity = result.scalars().first()
                
                # Get guild icon URL
                icon_url = str(guild.icon.url) if guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png"
                
                if guild_entity:
                    # Update existing guild
                    guild_entity.name = guild.name
                    guild_entity.icon_url = icon_url
                    guild_entity.member_count = len(guild.members)
                else:
                    # Create new guild
                    guild_entity = GuildEntity(
                        guild_id=str(guild.id),
                        name=guild.name,
                        icon_url=icon_url,
                        member_count=len(guild.members)
                    )
                    session.add(guild_entity)
                
                await session.commit()
                logger.info(f"Synchronized guild {guild.name} to database")
        except Exception as e:
            logger.error(f"Error synchronizing guild {guild.name} to database: {e}")

    async def sync_guild_members(self, guild: Guild) -> None:
        """Sync all members from a guild to the database"""
        try:
            # First sync the guild itself
            await self.sync_guild_to_database(guild)
            
            members = guild.members
            logger.info(f"[Guild:{guild.id}] Starting sync of {len(members)} members from guild {guild.name}")
            
            synced_count = 0
            skipped_count = 0
            error_count = 0
            
            async with session_context() as session:
                 # Instantiate repo inside session
                 user_repo = UserRepositoryImpl(session)
                 for member in members:
                     try:             
                         user_data = {
                             'discord_id': member.id,
                             'username': member.name,
                             'discriminator': member.discriminator,
                             'guild_id': str(guild.id),  # Convert to string for consistency
                             'is_bot': member.bot,
                             'joined_at': member.joined_at,
                             'nickname': member.nick,
                             'avatar': str(member.avatar.url) if member.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
                         }
                         
                         if member.bot:
                             skipped_count += 1
                             continue
                         
                         await user_repo.create_or_update(user_data)
                         synced_count += 1
                         
                     except Exception as e:
                         error_count += 1
                         logger.error(f"[Guild:{guild.id}] Failed to sync member {member.name} (ID: {member.id}): {e}", exc_info=True)
                         continue
            
            # Log final statistics
            logger.info(f"[Guild:{guild.id}] Guild {guild.name} sync complete:")
            logger.info(f"[Guild:{guild.id}] - Total members processed: {len(members)}")
            logger.info(f"[Guild:{guild.id}] - Successfully synced: {synced_count}")
            logger.info(f"[Guild:{guild.id}] - Skipped (bots): {skipped_count}")
            logger.info(f"[Guild:{guild.id}] - Errors: {error_count}")
            
        except Exception as e:
            logger.error(f"[Guild:{guild.id}] Failed to sync members for guild {guild.name}: {e}", exc_info=True)

    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup resources for a specific guild"""
        logger.info(f"Cleaning up user workflow for guild {guild_id}")
        await super().cleanup_guild(guild_id)

    async def cleanup(self) -> None:
        """Cleanup all resources"""
        logger.info("Cleaning up user workflow")
        await super().cleanup() 