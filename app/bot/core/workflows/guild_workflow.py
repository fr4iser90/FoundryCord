# app/bot/core/workflows/guild_workflow.py
from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord import GuildEntity
from sqlalchemy import select

logger = get_bot_logger()

class GuildWorkflow(BaseWorkflow):
    """Workflow for managing Discord guilds"""
    
    def __init__(self, database_workflow, bot=None):
        super().__init__(bot)
        self.name = "guild"
        self.database_workflow = database_workflow
        self.bot = bot
        
        # Add dependencies
        self.add_dependency("database")
    
    async def initialize(self) -> bool:
        """Initialize the guild workflow"""
        logger.info("Initializing guild workflow")
        
        try:
            # Sync all guilds the bot is connected to
            if self.bot:
                for guild in self.bot.guilds:
                    await self.sync_guild(guild)
            
            logger.info("Guild workflow initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize guild workflow: {str(e)}")
            return False
    
    async def sync_guild(self, guild):
        """Synchronize guild data to database"""
        try:
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
                    guild_entity.owner_id = str(guild.owner_id) if guild.owner_id else None
                    guild_entity.member_count = len(guild.members)
                else:
                    # Create new guild
                    guild_entity = GuildEntity(
                        guild_id=str(guild.id),
                        name=guild.name,
                        icon_url=icon_url,
                        owner_id=str(guild.owner_id) if guild.owner_id else None,
                        member_count=len(guild.members)
                    )
                    session.add(guild_entity)
                
                await session.commit()
                logger.info(f"Synchronized guild {guild.name} to database")
                return guild_entity
        except Exception as e:
            logger.error(f"Error synchronizing guild {guild.name} to database: {e}")
            return None
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up guild workflow resources")
        # Nothing to clean up for now