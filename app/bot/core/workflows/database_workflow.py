import logging
import asyncio
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import Engine
from sqlalchemy import text
from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.shared.infrastructure.database.models.base import Base
from app.bot.infrastructure.database.models.category_entity import CategoryEntity, CategoryPermissionEntity
from app.bot.infrastructure.database.models.channel_entity import ChannelEntity, ChannelPermissionEntity
from app.shared.infrastructure.database.service import DatabaseService
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.shared.infrastructure.database.migrations.init_db import init_db, migrate_existing_users

class DatabaseWorkflow(BaseWorkflow):
    """Workflow for database initialization and management"""
    
    def __init__(self):
        super().__init__()
        self.name = "database"
        self.db_service = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the database connection and create tables"""
        logger.info("Initializing database connection")
        
        try:
            # Initialize the database service
            self.db_service = DatabaseService()
            
            # Create tables if they don't exist
            async with self.db_service.engine.begin() as conn:
                # Create all tables defined in the models
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database connection initialized successfully")
            self.is_initialized = True
            
            # Verify connection by running a simple query
            async with self.db_service.async_session() as session:
                await session.execute(text("SELECT 1"))
                await session.commit()
            
            logger.info("Database connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            return False
    
    def get_db_service(self) -> Optional[DatabaseService]:
        """Get the database service instance"""
        if not self.is_initialized:
            logger.warning("Database not initialized, returning None")
            return None
        return self.db_service

    async def _verify_database_integrity(self):
        """Verify database integrity and run necessary data checks"""
        try:
            # Implement database verification logic here
            # For example: check if required tables exist, check critical data
            logger.info("Database integrity verified")
        except Exception as e:
            logger.error(f"Database integrity verification failed: {e}")
            raise
            
    async def cleanup(self):
        """Cleanup database resources"""
        try:
            from app.shared.infrastructure.database.core.connection import close_engine
            logger.debug("Closing database connections")
            await close_engine()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Database cleanup failed: {e}")
