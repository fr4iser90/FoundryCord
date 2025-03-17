import logging
import asyncio
from typing import Dict, Any, Optional
import nextcord  # Geändert von discord zu nextcord

from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class DatabaseWorkflow(BaseWorkflow):
    """Workflow for database operations"""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.name = "database"
        self.db_service = None
    
    async def initialize(self):
        """Initialize the database workflow"""
        logger.info("Initializing database connection")
        
        try:
            # Import database service
            from app.shared.infrastructure.database.service import DatabaseService
            
            # Create database service
            self.db_service = DatabaseService()
            
            # Verify database connection - DatabaseService doesn't have initialize()
            # so we'll just check if it's ready directly
            for attempt in range(1, 6):
                logger.info(f"Verifying database connection (attempt {attempt}/5)...")
                if await self.db_service.is_ready():
                    logger.info("Database connection verified successfully")
                    return True
                
                if attempt < 5:
                    logger.warning(f"Database not ready, retrying in 2 seconds...")
                    await asyncio.sleep(2)
            
            logger.error("Failed to verify database connection after 5 attempts")
            return False
            
        except Exception as e:
            logger.error(f"Error initializing database workflow: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def cleanup(self):
        """Cleanup database resources"""
        logger.info("Cleaning up database resources")
        
        try:
            if self.db_service:
                # Check if cleanup method exists before calling it
                if hasattr(self.db_service, 'cleanup') and callable(self.db_service.cleanup):
                    await self.db_service.cleanup()
                else:
                    # If no cleanup method, try to close connections if possible
                    if hasattr(self.db_service, 'close') and callable(self.db_service.close):
                        await self.db_service.close()
            
            logger.info("Database resources cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up database resources: {e}")
    
    def get_db_service(self):
        """Get the database service"""
        return self.db_service
