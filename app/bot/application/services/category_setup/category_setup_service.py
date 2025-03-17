"""Service for setting up and managing Discord categories."""
from typing import Dict, Any, List, Optional
import nextcord

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class CategorySetupService:
    """Service for managing Discord server categories."""
    
    def __init__(self, bot):
        self.bot = bot
        self.initialized = False
        self.default_categories = [
            "Information",
            "Announcements",
            "General",
            "Voice Channels",
            "Bot Commands",
            "Administration"
        ]
        
    async def initialize(self):
        """Initialize the category setup service."""
        self.initialized = True
        logger.info("Category setup service initialized")
        return True
        
    async def setup_default_categories(self, guild):
        """Set up default categories in a guild."""
        created_categories = []
        position = 0
        
        for category_name in self.default_categories:
            # Check if category exists
            existing = None
            for category in guild.categories:
                if category.name.lower() == category_name.lower():
                    existing = category
                    break
                    
            if existing:
                logger.debug(f"Category already exists: {category_name}")
                created_categories.append(existing)
            else:
                # Create category
                try:
                    category = await guild.create_category(name=category_name, position=position)
                    logger.info(f"Created category: {category_name}")
                    created_categories.append(category)
                except Exception as e:
                    logger.error(f"Error creating category {category_name}: {e}")
                    
            position += 1
            
        return created_categories
        
    async def create_category(self, guild, name, position=0):
        """Create a category in a guild."""
        try:
            category = await guild.create_category(name=name, position=position)
            logger.info(f"Created category: {name}")
            return category
        except Exception as e:
            logger.error(f"Error creating category {name}: {e}")
            return None
        
    async def delete_category(self, category):
        """Delete a category."""
        try:
            await category.delete()
            logger.info(f"Deleted category: {category.name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting category {category.name}: {e}")
            return False
            
    async def update_category(self, category, **kwargs):
        """Update a category's settings."""
        try:
            await category.edit(**kwargs)
            logger.info(f"Updated category: {category.name}")
            return True
        except Exception as e:
            logger.error(f"Error updating category {category.name}: {e}")
            return False 