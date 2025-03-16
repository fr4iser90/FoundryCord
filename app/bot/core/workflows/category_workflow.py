from .base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.config.constants.category_constants import CATEGORIES

class CategoryWorkflow(BaseWorkflow):
    async def initialize(self):
        """Initialize category workflow"""
        try:
            logger.debug("Starting category workflow initialization")
            logger.debug(f"Category config available? {hasattr(self.bot, 'category_config')}")
            
            if not hasattr(self.bot, 'category_config'):
                # Handle missing config
                from app.bot.infrastructure.config.category_config import CategoryConfig
                logger.warning("Category config not found, registering it now")
                self.bot.category_config = CategoryConfig.register(self.bot)
            
            # Create category setup through factory (similar to service pattern)
            category_setup = self.bot.factory.create_service(
                "Category Setup",
                self.bot.category_config['setup']
            )
            
            # Initialize using lifecycle manager's service initializer
            await self.bot.lifecycle._initialize_service(category_setup)
            self.bot.category_setup = category_setup
            
            # Add category integrity check
            await self._verify_category_integrity()

            return category_setup
            
        except Exception as e:
            logger.error(f"Category workflow initialization failed: {e}")
            raise
            
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
            
    async def cleanup(self):
        """Cleanup category resources"""
        try:
            if self.bot.category_setup:
                # Add cleanup logic if needed
                logger.info("Category cleanup completed")
        except Exception as e:
            logger.error(f"Category cleanup failed: {e}")
