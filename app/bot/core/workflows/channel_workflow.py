import logging
import nextcord
import asyncio
from typing import Dict, Optional, List
from sqlalchemy import text

from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.bot.core.workflows.category_workflow import CategoryWorkflow
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class ChannelWorkflow(BaseWorkflow):
    """Workflow for channel setup and management"""
    
    def __init__(self, category_workflow: CategoryWorkflow, database_workflow: DatabaseWorkflow):
        super().__init__()
        self.name = "channel"
        self.category_workflow = category_workflow
        self.database_workflow = database_workflow
        self.channel_repository = None
        self.channel_setup_service = None
        
        # Define dependencies
        self.add_dependency("category")
        self.add_dependency("database")
    
    async def initialize(self):
        """Initialize the channel workflow"""
        logger.info("Initializing channel workflow")
        
        try:
            # Get the database service
            db_service = self.database_workflow.get_db_service()
            if not db_service:
                logger.error("Database service not available, cannot initialize channel workflow")
                return False
                
            # Import repositories and services
            from app.bot.infrastructure.repositories.channel_repository_impl import ChannelRepositoryImpl
            from app.bot.application.services.channel.channel_builder import ChannelBuilder
            from app.bot.application.services.channel.channel_setup_service import ChannelSetupService
            from app.shared.infrastructure.database.migrations.channels.seed_channels import check_and_seed_channels
            
            # Get the category repository from the category workflow
            category_repository = self.category_workflow.get_category_repository()
            
            # Create channel repository
            self.channel_repository = ChannelRepositoryImpl(db_service)
            
            # Check if the channels table exists and has the correct schema
            engine = db_service.get_engine()
            try:
                # Check if the channels table exists
                table_exists = False
                async with engine.connect() as conn:
                    result = await conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'channels'
                        )
                    """))
                    row = result.first()
                    table_exists = row[0] if row else False
                
                # Check if discord_id and category_discord_id columns are BigInteger
                if table_exists:
                    async with engine.connect() as conn:
                        result = await conn.execute(text("""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE table_name = 'channels' AND column_name IN ('discord_id', 'category_discord_id')
                        """))
                        columns = {row[0]: row[1] for row in result}
                        
                        # If columns exist but are not bigint, drop the table to recreate it
                        if ('discord_id' in columns and columns['discord_id'].lower() != 'bigint') or \
                           ('category_discord_id' in columns and columns['category_discord_id'].lower() != 'bigint'):
                            logger.info("Channel table exists but has incorrect column types, recreating...")
                            table_exists = False
                            async with engine.begin() as conn:
                                await conn.execute(text("DROP TABLE IF EXISTS channel_permissions CASCADE"))
                                await conn.execute(text("DROP TABLE IF EXISTS channels CASCADE"))
                
                # Create the table if it doesn't exist or needs to be recreated
                if not table_exists:
                    logger.info("Creating channels table with correct schema")
                    # Import all models to make sure they're registered with the metadata
                    from app.bot.infrastructure.database.models import ChannelEntity, ChannelPermissionEntity
                    from app.shared.infrastructure.database.models.base import Base
                    
                    # Create all tables
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)
                    logger.info("Channels table created with correct column types")
                    
                    # Sleep briefly to ensure tables are fully created
                    await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Error checking/creating channels table: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False
                
            # Create channel builder with both repositories
            channel_builder = ChannelBuilder(
                self.channel_repository,
                category_repository
            )
            
            # Create channel setup service
            self.channel_setup_service = ChannelSetupService(
                self.channel_repository, 
                channel_builder,
                self.category_workflow
            )
            
            # Check if channels exist, if not seed the database
            try:
                check_and_seed_channels()
            except Exception as e:
                logger.error(f"Error checking/seeding channels: {e}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error initializing channel workflow: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def cleanup(self):
        """Cleanup resources used by the channel workflow"""
        logger.info("Cleaning up channel workflow resources")
        # Nothing to clean up for now
        
    async def setup_channels(self, guild: nextcord.Guild) -> Dict[str, nextcord.TextChannel]:
        """Set up all channels for the guild"""
        if not self.channel_setup_service:
            logger.error("Channel setup service not initialized")
            return {}
            
        logger.info(f"Setting up channels for guild: {guild.name}")
        return await self.channel_setup_service.setup_channels(guild)
    
    async def sync_with_discord(self, guild: nextcord.Guild) -> None:
        """Sync channels with existing Discord channels"""
        if not self.channel_setup_service:
            logger.error("Channel setup service not initialized")
            return
            
        logger.info(f"Syncing channels with Discord for guild: {guild.name}")
        await self.channel_setup_service.sync_with_discord(guild)

    def get_channel_repository(self):
        """Get the channel repository"""
        return self.channel_repository
    
    def get_channel_setup_service(self):
        """Get the channel setup service"""
        return self.channel_setup_service
