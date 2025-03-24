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
from app.bot.application.services.category.category_setup_service import CategorySetupService
from app.bot.application.services.category.category_builder import CategoryBuilder
from app.bot.domain.categories.repositories.category_repository import CategoryRepository
from app.shared.infrastructure.repositories.discord import CategoryRepositoryImpl

logger = get_bot_logger()

class CategoryWorkflow(BaseWorkflow):
    """Workflow for category setup and management"""
    
    def __init__(self, database_workflow: DatabaseWorkflow):
        super().__init__()
        self.name = "category"
        self.database_workflow = database_workflow
        self.category_repository = None
        self.category_service = None
        self.category_setup_service = None
        
        # Define dependencies
        self.add_dependency("database")
    
    async def initialize(self):
        """Initialize the category workflow"""
        try:
            # Verify categories exist
            async with session_context() as session:
                result = await session.execute(text("SELECT COUNT(*) FROM discord_categories"))
                count = result.scalar()
                
                if count == 0:
                    logger.error("No categories found. Please run database migrations first")
                    return False
                
                logger.info(f"Found {count} categories")
                
                # Initialize repository and services
                db_service = self.database_workflow.get_db_service()
                if not db_service:
                    logger.error("Database service not available")
                    return False
                
                # Create repository and services
                self.category_repository = CategoryRepositoryImpl(db_service)
                category_builder = CategoryBuilder(self.category_repository)
                self.category_setup_service = CategorySetupService(
                    self.category_repository,
                    category_builder
                )
                
                # Initialize the setup service
                await self.category_setup_service.initialize()
                
                # Maintain backwards compatibility with existing code
                self.category_service = self.category_setup_service
                
                return True
                
        except Exception as e:
            logger.error(f"Error initializing category workflow: {e}")
            traceback.print_exc()
            return False
    
    def get_category_repository(self):
        """Get the category repository"""
        return self.category_repository
    
    def get_category_service(self):
        """Get the category service (backward compatibility)"""
        return self.category_service
    
    def get_category_setup_service(self):
        """Get the category setup service"""
        return self.category_setup_service

    async def setup_categories(self, guild):
        """Set up all categories for the guild"""
        if not self.category_setup_service:
            logger.error("Category service not initialized")
            return {}
        
        logger.info(f"Setting up categories for guild: {guild.name}")
        return await self.category_setup_service.setup_categories(guild)
        
    async def sync_with_discord(self, guild: nextcord.Guild) -> None:
        """Sync categories with existing Discord categories"""
        if not self.category_setup_service:
            logger.error("Category service not initialized")
            return
            
        logger.info(f"Syncing categories with Discord for guild: {guild.name}")
        await self.category_setup_service.sync_with_discord(guild)
