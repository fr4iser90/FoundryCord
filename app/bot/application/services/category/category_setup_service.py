import discord
import logging
from typing import Dict, List, Optional
import asyncio
from app.shared.domain.repositories.discord.category_repository import CategoryRepository
from app.bot.application.services.category.category_builder import CategoryBuilder
from app.shared.infrastructure.models.discord.entities.category_entity import CategoryEntity
from app.shared.infrastructure.models.discord.enums.category import CategoryPermissionLevel
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class CategorySetupService:
    """Service for setting up Discord categories"""
    
    def __init__(self, category_repository: CategoryRepository, category_builder: CategoryBuilder):
        """Initialize the category setup service"""
        self.category_repository = category_repository
        self.category_builder = category_builder
        self.categories_cache = {}
    
    def get_category_repository(self) -> CategoryRepository:
        """Get the category repository."""
        return self.category_repository
    
    async def setup_categories(self, guild: discord.Guild) -> Dict[str, discord.CategoryChannel]:
        """Set up all categories for the guild"""
        # Get all categories from the repository
        categories = await self.category_repository.get_enabled_categories()
        
        if not categories:
            logger.warning(f"No categories found in the database")
            return {}
            
        logger.info(f"Setting up {len(categories)} categories for guild {guild.name}")
        
        # Set up each category and track the results
        result = {}
        for category in categories:
            discord_category = await self.setup_category(guild, category)
            if discord_category:
                result[category.name] = discord_category
        
        return result
    
    async def setup_category(self, guild: discord.Guild, category_model: CategoryEntity) -> Optional[discord.CategoryChannel]:
        """Set up a single category in the guild"""
        logger.info(f"Setting up category: {category_model.name}")
        
        # Check if the category already exists in Discord
        existing_by_id = None
        existing_by_name = None
        
        if category_model.discord_id:
            existing_by_id = discord.utils.get(guild.categories, id=category_model.discord_id)
            
        if not existing_by_id:
            existing_by_name = discord.utils.get(guild.categories, name=category_model.name)
        
        # If the category exists, update it
        if existing_by_id:
            logger.info(f"Found existing category with ID {category_model.discord_id}")
            # Update the category in Discord if needed
            # For now, just return the existing category
            return existing_by_id
            
        elif existing_by_name:
            logger.info(f"Found existing category with name {category_model.name} (ID: {existing_by_name.id})")
            # Update the database with the Discord ID
            await self.category_repository.update_discord_id(category_model.id, existing_by_name.id)
            await self.category_repository.update_category_status(category_model.id, True)
            logger.info(f"Updated category {category_model.name} with Discord ID {existing_by_name.id}")
            return existing_by_name
            
        else:
            # Create the category in Discord
            logger.info(f"Creating new category: {category_model.name}")
            try:
                discord_category = await self.category_builder.create_category(guild, category_model)
                if discord_category:
                    # Update the database with the Discord ID
                    await self.category_repository.update_discord_id(category_model.id, discord_category.id)
                    await self.category_repository.update_category_status(category_model.id, True)
                    logger.info(f"Created category {category_model.name} with Discord ID {discord_category.id}")
                    return discord_category
                else:
                    logger.error(f"Failed to create category: {category_model.name}")
                    return None
            except Exception as e:
                logger.error(f"Error creating category {category_model.name}: {str(e)}")
                return None
    
    async def sync_with_discord(self, guild: discord.Guild) -> None:
        """Sync categories with existing Discord categories"""
        
        # Get all categories from the repository
        categories = await self.category_repository.get_all_categories()
        
        # Get all Discord categories
        discord_categories = guild.categories
        
        # Map Discord categories by name
        discord_categories_by_name = {c.name: c for c in discord_categories}
        
        # Update database categories with Discord IDs
        for category in categories:
            if category.name in discord_categories_by_name:
                discord_category = discord_categories_by_name[category.name]
                
                # Update the database with the Discord ID
                if category.discord_id != discord_category.id:
                    logger.info(f"Updating Discord ID for category {category.name} from {category.discord_id} to {discord_category.id}")
                    await self.category_repository.update_discord_id(category.id, discord_category.id)
                    await self.category_repository.mark_as_created(category.id)
                    
                # Update position if changed
                if category.position != discord_category.position:
                    logger.info(f"Updating position for category {category.name} from {category.position} to {discord_category.position}")
                    await self.category_repository.update_position(category.id, discord_category.position)
    
    async def get_category_by_name(self, name: str) -> Optional[CategoryEntity]:
        """
        Get a category model by name from cache or database
        """
        if name in self.categories_cache:
            return self.categories_cache[name]
        
        category = await self.category_repository.get_category_by_name(name)
        if category:
            self.categories_cache[name] = category
        return category
    
    async def refresh_cache(self) -> None:
        """
        Refresh the categories cache
        """
        self.categories_cache.clear()
        categories = await self.category_repository.get_all_categories()
        for category in categories:
            self.categories_cache[category.name] = category
    
    async def initialize(self):
        """Initialize the category setup service."""
        logger.info("Initializing category setup service")
        # Load categories from database
        self.categories_cache = {}
        categories = await self.category_repository.get_all_categories()
        for category in categories:
            self.categories_cache[category.name] = category
        logger.info(f"Loaded {len(categories)} categories into cache")
        return True 