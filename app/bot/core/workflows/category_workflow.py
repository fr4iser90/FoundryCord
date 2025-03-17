from .base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.config.constants.category_constants import CATEGORIES
from typing import Dict, Any, List
import asyncio

class CategoryWorkflow(BaseWorkflow):
    """Workflow for managing Discord category operations."""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.category_setup_service = None
        
    async def initialize(self):
        """Initialize the category workflow."""
        try:
            # Try to get category setup service
            # If service creation fails, we'll handle gracefully
            try:
                category_setup = {
                    'name': 'category_setup',
                    'type': 'category_setup'
                }
                self.category_setup_service = await self.bot.lifecycle._initialize_service(category_setup)
            except Exception as e:
                logger.error(f"Failed to initialize category setup service: {e}")
                # Continue without the service
                
            # Initialize with a default if service is not available
            if not self.category_setup_service:
                logger.warning("Category setup service not available, using defaults")
                # Could set default categories here if needed
                
            logger.info("Category workflow initialized")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing category workflow: {e}")
            return False
            
    async def create_category(self, guild, name, position=0):
        """Create a category in a guild."""
        try:
            if self.category_setup_service and hasattr(self.category_setup_service, 'create_category'):
                return await self.category_setup_service.create_category(guild, name, position)
            else:
                # Fallback implementation
                category = await guild.create_category(name=name, position=position)
                logger.info(f"Created category: {name}")
                return category
                
        except Exception as e:
            logger.error(f"Error creating category {name}: {e}")
            return None
            
    async def get_or_create_category(self, guild, name, position=0):
        """Get an existing category or create a new one."""
        # Check if category exists
        for category in guild.categories:
            if category.name.lower() == name.lower():
                return category
                
        # Create category if it doesn't exist
        return await self.create_category(guild, name, position)
    
    async def cleanup(self):
        """Clean up category workflow resources."""
        logger.info("Category workflow cleaned up")
        return True

    async def _verify_category_integrity(self):
        """Verify all categories exist and repair if needed"""
        try:
            from app.bot.infrastructure.config.category_config import CategoryConfig
            from app.bot.infrastructure.config.constants.category_constants import CATEGORIES
            
            logger.info("Verifying category integrity...")
            
            # Check each category
            for category_key, category_config in CATEGORIES.items():
                if not await self.bot.category_setup.verify_category():
                    logger.warning(f"Category {category_config['name']} not found, attempting to create")
                    await self.bot.category_setup.ensure_category_exists()
            
            logger.info("Category integrity verification completed")
                
        except Exception as e:
            logger.error(f"Category integrity verification failed: {e}")
