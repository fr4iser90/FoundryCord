from typing import List
import logging
from nextcord import Guild, Member
from app.shared.infrastructure.models.discord.entities.guild_user_entity import GuildUserEntity
from app.shared.domain.repositories.auth.user_repository import UserRepository
from .base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class UserWorkflow(BaseWorkflow):
    """Workflow for managing Discord users"""
    
    def __init__(self, database_workflow, bot=None):
        super().__init__()
        self.name = "user"
        self.database_workflow = database_workflow
        self.user_repository = None
        self.bot = bot
        
        # Add dependencies
        self.add_dependency("database")
    
    async def initialize(self) -> bool:
        """Initialize the user workflow"""
        logger.info("Initializing user workflow")
        
        try:
            # Initialize user repository
            from app.shared.infrastructure.repositories.auth.user_repository_impl import UserRepositoryImpl
            from app.shared.infrastructure.database.session.context import session_context
            
            async with session_context() as session:
                self.user_repository = UserRepositoryImpl(session)
            
            # Start syncing for all guilds
            if hasattr(self, 'bot') and self.bot:
                for guild in self.bot.guilds:
                    await self.sync_guild_members(guild)
            
            logger.info("User workflow initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize user workflow: {str(e)}")
            return False

    async def sync_guild_members(self, guild: Guild) -> None:
        """Sync all members from a guild to the database"""
        try:
            members = guild.members
            logger.info(f"Starting sync of {len(members)} members from guild {guild.name}")
            
            synced_count = 0
            skipped_count = 0
            error_count = 0
            
            for member in members:
                try:
                    # Debug log for each member being processed
                    logger.debug(f"Processing member: {member.name}#{member.discriminator} (ID: {member.id})")
                    
                    user_data = {
                        'discord_id': member.id,
                        'username': member.name,
                        'discriminator': member.discriminator,
                        'guild_id': guild.id,
                        'is_bot': member.bot,
                        'joined_at': member.joined_at,
                        'nickname': member.nick
                    }
                    
                    if member.bot:
                        logger.debug(f"Skipping bot user: {member.name}")
                        skipped_count += 1
                        continue
                        
                    await self.user_repository.create_or_update(user_data)
                    synced_count += 1
                    logger.debug(f"Successfully synced user: {member.name}")
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Failed to sync member {member.name}: {str(e)}")
                    continue
            
            # Log final statistics
            logger.info(f"Guild {guild.name} sync complete:")
            logger.info(f"- Total members processed: {len(members)}")
            logger.info(f"- Successfully synced: {synced_count}")
            logger.info(f"- Skipped (bots): {skipped_count}")
            logger.info(f"- Errors: {error_count}")
            
        except Exception as e:
            logger.error(f"Failed to sync guild members: {str(e)}")

    async def cleanup(self) -> None:
        """Cleanup user workflow resources"""
        logger.info("Cleaning up user workflow")
        # No specific cleanup needed for now 