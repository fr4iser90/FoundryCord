import discord
import logging
from typing import Dict, List, Optional
from app.bot.domain.categories.repositories.category_repository import CategoryRepository
from app.bot.application.services.category.category_builder import CategoryBuilder
from app.bot.domain.categories.models.category_model import CategoryModel

logger = logging.getLogger(__name__)

class CategorySetupService:
    """Service for managing Discord category setup and synchronization"""
    
    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository
        self.category_builder = CategoryBuilder(category_repository)
        self.categories_cache: Dict[str, CategoryModel] = {}
    
    async def setup_categories(self, guild: discord.Guild) -> Dict[str, discord.CategoryChannel]:
        """
        Set up all categories for the guild and return a mapping of category names to Discord category channels
        """
        logger.info(f"Setting up categories for guild: {guild.name}")
        
        # Load all enabled categories from the database
        db_categories = self.category_repository.get_enabled_categories()
        for category in db_categories:
            self.categories_cache[category.name] = category
        
        # Set up categories in Discord
        discord_categories = await self.category_builder.setup_all_categories(guild)
        
        # Create a mapping of category names to Discord category channels
        category_map = {category.name: category for category in discord_categories}
        
        logger.info(f"Successfully set up {len(category_map)} categories")
        return category_map
    
    async def sync_with_discord(self, guild: discord.Guild) -> None:
        """
        Synchronize database categories with existing Discord categories
        """
        logger.info(f"Syncing categories with Discord for guild: {guild.name}")
        await self.category_builder.sync_categories(guild)
        logger.info("Category synchronization completed")
    
    def get_category_by_name(self, name: str) -> Optional[CategoryModel]:
        """
        Get a category model by name from cache or database
        """
        if name in self.categories_cache:
            return self.categories_cache[name]
        
        category = self.category_repository.get_category_by_name(name)
        if category:
            self.categories_cache[name] = category
        
        return category
    
    def refresh_cache(self) -> None:
        """
        Refresh the categories cache
        """
        self.categories_cache.clear()
        categories = self.category_repository.get_all_categories()
        for category in categories:
            self.categories_cache[category.name] = category 