import logging
import nextcord
import asyncio
from typing import Dict, Optional, List
from sqlalchemy import text
import traceback

from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session.context import session_context

logger = get_bot_logger()

class CategoryWorkflow(BaseWorkflow):
    """Workflow for category setup and management"""
    
    def __init__(self, database_workflow: DatabaseWorkflow):
        super().__init__()
        self.name = "category"
        self.database_workflow = database_workflow
        self.category_repository = None
        self.category_service = None
        
        # Define dependencies
        self.add_dependency("database")
    
    async def initialize(self):
        """Initialize the category workflow"""
        try:
            # Verify categories exist
            async with session_context() as session:
                result = await session.execute(text("SELECT COUNT(*) FROM categories"))
                count = result.scalar()
                
                if count == 0:
                    logger.error("No categories found. Please run database migrations first")
                    return False
                    
                logger.info(f"Found {count} categories")
                return True
                
        except Exception as e:
            logger.error(f"Error verifying categories: {e}")
            return False
    
    def get_category_repository(self):
        """Get the category repository"""
        return self.category_repository
    
    def get_category_service(self):
        """Get the category service"""
        return self.category_service

    async def setup_categories(self, guild):
        """Set up all categories for the guild"""
        if not self.category_service:
            logger.error("Category service not initialized")
            return {}
        
        logger.info(f"Setting up categories for guild: {guild.name}")
        return await self.category_service.setup_categories(guild)
        
    async def sync_with_discord(self, guild: nextcord.Guild) -> None:
        """Sync categories with existing Discord categories"""
        if not self.category_service:
            logger.error("Category service not initialized")
            return
            
        logger.info(f"Syncing categories with Discord for guild: {guild.name}")
        await self.category_service.sync_with_discord(guild)
