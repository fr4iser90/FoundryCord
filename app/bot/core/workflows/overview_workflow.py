import logging
import nextcord
from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.models import GuildEntity
from sqlalchemy import select, update
from sqlalchemy.orm import session

logger = get_bot_logger()

class OverviewWorkflow(BaseWorkflow):
    """Workflow for gathering an overview of the server"""

    def __init__(self, bot):
        super().__init__(bot)
        self.name = "overview"
        self.guild_data = {}

    async def initialize(self):
        """Initialize the overview workflow"""
        logger.info("Initializing overview workflow")
        try:
            for guild in self.bot.guilds:
                await self.collect_guild_data(guild)
            logger.info("Overview workflow initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Overview workflow initialization failed: {e}")
            return False
    #async def collect_guild_data(self, guild: nextcord.Guild):
    async def collect_guild_data(self, guild: nextcord.GuildEntity):
        """Collect data from the guild and store in database"""
        logger.info(f"Collecting data for guild: {guild.name}")
        
        # Store guild info
        async with session() as session:
            # 1. Update or create guild record
            # Check if guild exists
            query = select(GuildEntity).where(GuildEntity.guild_id == str(guild.id))
            result = await session.execute(query)
            guild_record = result.scalar_one_or_none()
            
            if guild_record:
                # Update existing record
                stmt = update(GuildEntity).where(
                    GuildEntity.guild_id == str(guild.id)
                ).values(
                    name=guild.name,
                    icon_url=str(guild.icon.url) if guild.icon else None,
                    owner_id=str(guild.owner_id) if guild.owner_id else None,
                    member_count=guild.member_count
                )
                await session.execute(stmt)
            else:
                # Create new guild record
                guild_record = GuildEntity(
                    guild_id=str(guild.id),
                    name=guild.name,
                    icon_url=str(guild.icon.url) if guild.icon else None,
                    owner_id=str(guild.owner_id) if guild.owner_id else None,
                    member_count=guild.member_count
                )
                session.add(guild_record)
            
            await session.commit()
            
            # 2. Synchronize members and their roles
            await self.sync_guild_members(guild, session)

    async def cleanup(self):
        """Cleanup resources used by the overview workflow"""
        logger.info("Cleaning up overview workflow resources")
        self.guild_data.clear()