from typing import Optional, Dict, List
from nextcord import Guild, CategoryChannel, PermissionOverwrite, utils
from app.shared.logging import logger
from app.shared.database.models.config import get_session
from app.shared.database.models import CategoryMapping
from sqlalchemy import select, update, insert
import asyncio
import os
from app.bot.infrastructure.config.constants.category_constants import CATEGORIES, CATEGORY_CHANNEL_MAPPINGS


class CategorySetupService:
    """Service for managing Discord category creation and verification"""
    
    def __init__(self, bot):
        self.bot = bot
        self.guild: Optional[Guild] = None
        self.categories = {}  # Store category mappings
        self._default_category = next(iter(CATEGORIES)) if CATEGORIES else None
        
    async def initialize(self):
        """Initialize the category service with guild connection"""
        if not self.bot.guilds:
            raise ValueError("Bot is not connected to any guilds")
        
        self.guild = self.bot.guilds[0]
        logger.info(f"Category service connected to guild: {self.guild.name}")
        
        # Initialize all categories from configuration
        for category_type, config in CATEGORIES.items():
            await self._initialize_category(category_type, config)

    async def _initialize_category(self, category_type: str, config: dict):
        """Initialize a single category by checking DB, server, or creating new"""
        try:
            # 1. Check database first
            category_id = await self._get_category_from_db(category_type)
            if category_id:
                category = self.guild.get_channel(int(category_id))
                if category:
                    self.categories[category_type] = category
                    logger.info(f"Found {category_type} category in DB: {category.name}")
                    return

            # 2. Search server for existing category by name
            category = await self._find_category_by_name(config['name'])
            if category:
                self.categories[category_type] = category
                await self._store_category_mapping(category.id, category_type)
                logger.info(f"Found existing {category_type} category on server: {category.name}")
                return

            # 3. Create new category
            category = await self._create_category(config['name'], config)
            if category:
                self.categories[category_type] = category
                await self._store_category_mapping(category.id, category_type)
                logger.info(f"Created new {category_type} category: {category.name}")

        except Exception as e:
            logger.error(f"Error initializing {category_type} category: {e}")

    async def _get_category_from_db(self, category_type: str) -> Optional[str]:
        """Get category ID from database"""
        try:
            async for session in get_session():
                result = await session.execute(
                    select(CategoryMapping).where(
                        CategoryMapping.guild_id == str(self.guild.id),
                        CategoryMapping.category_type == category_type
                    )
                )
                mapping = result.scalars().first()
                return mapping.category_id if mapping else None
        except Exception as e:
            logger.error(f"Error getting category from DB: {e}")
            return None

    async def _find_category_by_name(self, name: str) -> Optional[CategoryChannel]:
        """Find category in guild by name"""
        return utils.get(self.guild.categories, name=name.upper())

    async def _create_category(self, name: str, config: dict) -> Optional[CategoryChannel]:
        """Create a new category with specified configuration"""
        try:
            overwrites = {
                self.guild.default_role: PermissionOverwrite(
                    read_messages=not config.get('is_private', True)
                ),
                self.guild.me: PermissionOverwrite(
                    read_messages=True, 
                    manage_channels=True
                )
            }

            category = await self.guild.create_category(
                name=name.upper(),
                overwrites=overwrites,
                position=config.get('position', 0),
                reason="Homelab Bot category initialization"
            )
            return category
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            return None

    async def _store_category_mapping(self, category_id: int, category_type: str):
        """Store category mapping in database"""
        try:
            async for session in get_session():
                # Check if mapping exists
                result = await session.execute(
                    select(CategoryMapping).where(
                        CategoryMapping.guild_id == str(self.guild.id),
                        CategoryMapping.category_type == category_type
                    )
                )
                mapping = result.scalars().first()
                
                if mapping:
                    await session.execute(
                        update(CategoryMapping)
                        .where(
                            CategoryMapping.guild_id == str(self.guild.id),
                            CategoryMapping.category_type == category_type
                        )
                        .values(category_id=str(category_id))
                    )
                else:
                    new_mapping = CategoryMapping(
                        guild_id=str(self.guild.id),
                        category_id=str(category_id),
                        category_name=self.categories[category_type].name,
                        category_type=category_type
                    )
                    session.add(new_mapping)
                    
                await session.commit()
                logger.info(f"Stored {category_type} category mapping: {category_id}")
                
        except Exception as e:
            logger.error(f"Error storing category mapping: {e}")

    async def verify_category(self, category_key: str) -> bool:
        """Verify if configured category exists in Discord"""
        if not self.categories.get(category_key):
            logger.warning(f"No {category_key} category found")
            return False
            
        try:
            category = self.guild.get_channel(int(self.categories[category_key].id))
            if category and isinstance(category, CategoryChannel):
                logger.info(f"Verified {category_key} category exists: {category.name} (ID: {self.categories[category_key].id})")
                return True
            else:
                logger.warning(f"{category_key} category ID {self.categories[category_key].id} not found or not a category")
                return False
        except Exception as e:
            logger.error(f"Error verifying {category_key} category: {e}")
            return False
            
    async def ensure_category_exists(self, category_type: str = None) -> Optional[CategoryChannel]:
        """Ensure category exists, creating it if necessary"""
        try:
            # Use default category if none specified
            if category_type is None:
                category_type = self._default_category
                logger.info(f"No category specified, using default: {category_type}")

            # First verify if it exists
            if category_type in self.categories:
                exists = await self.verify_category(category_type)
                if exists:
                    return self.categories[category_type]

            # If not exists, create new category using config from CATEGORIES
            config = CATEGORIES.get(category_type)
            if not config:
                logger.error(f"No configuration found for category type: {category_type}")
                return None

            category = await self._create_category(config['name'], config)
            if category:
                self.categories[category_type] = category
                await self._store_category_mapping(category.id, category_type)
                logger.info(f"Category created/ensured: {category.name}")
                return category
            else:
                logger.error(f"Failed to create category: {category_type}")
                return None
            
        except Exception as e:
            logger.error(f"Error ensuring category exists: {e}")
            return None
            
    async def get_category(self, category_type: str = None) -> Optional[CategoryChannel]:
        """Get a category by type, using default if none specified"""
        if category_type is None:
            category_type = self._default_category
            
        return self.categories.get(category_type)

async def setup_category(bot):
    """Setup function for Discord category"""
    try:
        # Create the category service
        from .category_setup_service import CategorySetupService
        
        if not hasattr(bot, 'category_setup'):
            logger.info("Creating new CategorySetupService")
            bot.category_setup = CategorySetupService(bot)
        
        # Initialize if bot is ready
        if bot.is_ready():
            await bot.category_setup.initialize()
            await bot.category_setup.ensure_category_exists()
            
        logger.info("Discord category setup service registered")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing Discord category setup: {e}")
        return False