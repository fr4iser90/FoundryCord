import logging
import asyncio
from typing import Optional
from sqlalchemy import text
from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.shared.infrastructure.database.service import DatabaseService
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class DatabaseWorkflow(BaseWorkflow):
    """Workflow for database connection management - NOT for migrations"""
    
    def __init__(self, bot=None):
        super().__init__(bot)
        self.name = "database"
        self.db_service = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize database connection (NOT for table creation)"""
        logger.info("Initializing database connection")
        
        try:
            # Initialize the database service
            self.db_service = DatabaseService()
            
            # Verify connection with retry logic
            max_retries = 5
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Verifying database connection (attempt {attempt}/{max_retries})...")
                    
                    # Test the connection with a simple query
                    session = await self.db_service.async_session()
                    async with session as session:
                        await session.execute(text("SELECT 1"))
                        await session.commit()
                    
                    logger.info("Database connection verified successfully")
                    self.is_initialized = True
                    return True
                    
                except Exception as e:
                    if "Connect call failed" in str(e) and attempt < max_retries:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Database connection error: {str(e)}")
                        logger.info(f"Waiting {wait_time} seconds before retry...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Error verifying database connection: {str(e)}")
                        if attempt >= max_retries:
                            return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            return False
    
    def get_db_service(self) -> Optional[DatabaseService]:
        """Get the database service instance"""
        if not self.is_initialized:
            logger.warning("Database not initialized, returning None")
            return None
        return self.db_service

    async def verify_database_health(self) -> bool:
        """Verify database is healthy and accessible"""
        if not self.is_initialized or not self.db_service:
            logger.error("Database service not initialized")
            return False
            
        try:
            # Test the connection with a simple query
            session = await self.db_service.async_session()
            async with session as session:
                await session.execute(text("SELECT 1"))
                await session.commit()
            
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
            
    async def cleanup(self):
        """Cleanup database resources"""
        try:
            if self.db_service:
                await self.db_service.close()
                logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Database cleanup failed: {e}")
