import logging
import asyncio
from typing import Dict, Any, Optional
import nextcord  # Geändert von discord zu nextcord
from sqlalchemy import text  # Wichtig: text direkt importieren

from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session.context import session_context  # Add this import

logger = get_bot_logger()

class DatabaseWorkflow(BaseWorkflow):
    """Workflow for database operations"""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.name = "database"
        self.db_service = None
    
    async def initialize(self):
        """Initialize the database workflow"""
        try:
            # ONLY verify data exists
            async with session_context() as session:
                # Check if required tables exist and have data
                tables = ['categories', 'channels', 'dashboards']
                for table in tables:
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    if count == 0:
                        logger.error(f"No data found in {table}. Please initialize database from web interface")
                        return False
            
            # Important: Initialize the db_service here
            from app.shared.infrastructure.database.service import DatabaseService
            self.db_service = DatabaseService(session)
            
            logger.info("Database verification successful")
            return True
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup database resources"""
        logger.info("Cleaning up database resources")
        
        try:
            if self.db_service:
                await self.db_service.close()
            logger.info("Database resources cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up database resources: {e}")
    
    def get_db_service(self):
        """Get the database service"""
        return self.db_service
