import logging
import discord
from typing import Dict, Optional, List
from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.bot.domain.categories.repositories.category_repository import CategoryRepository
from app.bot.infrastructure.repositories.category_repository_impl import CategoryRepositoryImpl
from app.bot.application.services.category.category_builder import CategoryBuilder
from app.bot.application.services.category.category_setup_service import CategorySetupService
from app.shared.infrastructure.database.migrations.categories.seed_categories import seed_categories

logger = logging.getLogger("homelab.bot")

class CategoryWorkflow(BaseWorkflow):
    """Workflow for category setup and management"""
    
    def __init__(self, database_workflow: DatabaseWorkflow):
        super().__init__()
        self.name = "category"
        self.database_workflow = database_workflow
        self.category_repository = None
        self.category_setup_service = None
    
    async def initialize(self):
        """Initialize the category workflow"""
        logger.info("Initializing category workflow")
        
        # Get the database service
        db_service = self.database_workflow.get_db_service()
        if not db_service:
            logger.error("Database service not available, cannot initialize category workflow")
            return False
        
        # Create the repository
        self.category_repository = CategoryRepositoryImpl(db_service)
        
        # Create the category builder - pass the repository here
        category_builder = CategoryBuilder(self.category_repository)
        
        # Create the category setup service
        self.category_setup_service = CategorySetupService(self.category_repository, category_builder)
        
        # Check if any categories exist, if not seed the database
        categories = self.category_repository.get_all_categories()
        if not categories:
            logger.info("No categories found in database, seeding default categories")
            # Use the seed function from the migration script
            seed_categories()
            logger.info("Default categories seeded successfully")
            
        return True
    
    async def cleanup(self):
        """Cleanup resources used by the category workflow"""
        logger.info("Cleaning up category workflow resources")
        # Not much to clean up here since we don't have any persistent connections
        # Just reset the objects
        self.category_repository = None
        self.category_setup_service = None
    
    async def setup_categories(self, guild: discord.Guild) -> Dict[str, discord.CategoryChannel]:
        """Set up all categories for the guild"""
        if not self.category_setup_service:
            logger.error("Category setup service not initialized")
            return {}
        
        logger.info(f"Setting up categories for guild: {guild.name}")
        return await self.category_setup_service.setup_categories(guild)
    
    async def sync_with_discord(self, guild: discord.Guild) -> None:
        """Sync categories with existing Discord categories"""
        if not self.category_setup_service:
            logger.error("Category setup service not initialized")
            return
        
        logger.info(f"Syncing categories with Discord for guild: {guild.name}")
        await self.category_setup_service.sync_with_discord(guild)
    
    def get_category_repository(self) -> Optional[CategoryRepository]:
        """Get the category repository"""
        return self.category_repository
    
    def get_category_setup_service(self) -> Optional[CategorySetupService]:
        """Get the category setup service"""
        return self.category_setup_service
