from typing import Dict, Optional
from app.bot.infrastructure.logging import logger
from app.bot.infrastructure.discord.category_setup_service import CategorySetupService
from app.bot.infrastructure.database.models import CategoryMapping
from app.bot.infrastructure.database.models.config import get_session
from sqlalchemy import select, update
from app.bot.infrastructure.config.constants.category_constants import CATEGORIES, ENABLE_HOMELAB_CATEGORY, ENABLE_GAMESERVERS_CATEGORY
from app.bot.infrastructure.config.env_config import EnvConfig
import os

class CategoryConfig:
    # Category ID loaded from EnvConfig
    HOMELAB_CATEGORY_ID = None
    GAMESERVERS_CATEGORY_ID = None
    DISCORD_SERVER = None
    
    # Constants from category_constants
    CATEGORIES = CATEGORIES
    ENABLE_HOMELAB_CATEGORY = ENABLE_HOMELAB_CATEGORY
    ENABLE_GAMESERVERS_CATEGORY = ENABLE_GAMESERVERS_CATEGORY
    
    # Default category name
    DEFAULT_CATEGORY_NAME = "HOMELAB"


    @classmethod
    async def create_category_setup(cls, bot) -> 'CategorySetupService':
        """Creates and configures the category setup service"""
        try:
            # Load from bot.env_config
            cls.HOMELAB_CATEGORY_ID = bot.env_config.HOMELAB_CATEGORY_ID
            cls.DISCORD_SERVER = bot.env_config.guild_id
            
            # Import here to avoid circular imports
            from app.bot.infrastructure.discord.category_setup_service import CategorySetupService
            
            # Load existing category mapping from app.bot.database
            async for session in get_session():
                result = await session.execute(
                    select(CategoryMapping).where(
                        CategoryMapping.guild_id == str(cls.DISCORD_SERVER)
                    )
                )
                mapping = result.scalars().first()
                
                if mapping:
                    logger.info(f"Found category mapping in database: {mapping.category_id}")
                    # Update config with database value if needed
                    if not cls.HOMELAB_CATEGORY_ID and mapping.category_id:
                        cls.HOMELAB_CATEGORY_ID = mapping.category_id
                        logger.info(f"Updated category ID from app.bot.database: {cls.HOMELAB_CATEGORY_ID}")
            
            category_setup = CategorySetupService(bot)
            return category_setup
            
        except Exception as e:
            logger.error(f"Failed to create category setup: {e}")
            raise

    @staticmethod
    def register(bot) -> Dict:
        """Register the category setup service with the bot"""
        async def setup(bot):
            try:
                category_setup = await CategoryConfig.create_category_setup(bot)
                await category_setup.initialize()
                await category_setup.ensure_category_exists()
                logger.info("Category setup service created and initialized successfully")
                return category_setup
            except Exception as e:
                logger.error(f"Failed to setup category service: {e}")
                raise
                
        return {
            "name": "Category Setup",
            "setup": setup
        }