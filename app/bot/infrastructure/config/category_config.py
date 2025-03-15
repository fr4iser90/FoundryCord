from typing import Dict, Optional
from app.shared.logging import logger
from app.shared.infrastructure.database.models import CategoryMapping
from app.shared.infrastructure.database.models.config import get_session
from sqlalchemy import select, update
from app.bot.infrastructure.config.constants.category_constants import CATEGORIES
from app.bot.infrastructure.config.env_config import EnvConfig
import os

class CategoryConfig:
    DISCORD_SERVER = None
    CATEGORIES = CATEGORIES

    @classmethod
    async def create_category_setup(cls, bot) -> 'CategorySetupService':
        """Creates and configures the category setup service"""
        try:
            cls.DISCORD_SERVER = bot.env_config.guild_id
            # Import here to avoid circular imports
            from app.bot.infrastructure.discord.category_setup_service import CategorySetupService
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
                # Import here to avoid circular imports
                from app.bot.infrastructure.discord.category_setup_service import CategorySetupService
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