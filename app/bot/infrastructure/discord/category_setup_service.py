from typing import Optional
from nextcord import Guild, CategoryChannel, PermissionOverwrite
from infrastructure.logging import logger
from infrastructure.database.models.config import get_session
from infrastructure.database.models import CategoryMapping
from sqlalchemy import select, update, insert
import asyncio
import os



class CategorySetupService:
    """Service for managing Discord category creation and verification"""
    
    def __init__(self, bot):
        self.bot = bot
        self.guild: Optional[Guild] = None
        self.category: Optional[CategoryChannel] = None
        self.category_id = None
        
    async def initialize(self):
        """Initialize the category service with guild connection"""
        if not self.bot.guilds:
            raise ValueError("Bot is not connected to any guilds")
        
        self.guild = self.bot.guilds[0]
        logger.info(f"Category service connected to guild: {self.guild.name}")
        
        # Get category ID from config
        self.category_id = self.bot.env_config.HOMELAB_CATEGORY_ID
        logger.info(f"Configured category ID: {self.category_id}")
        
    async def verify_category(self, category_key: str) -> bool:
        """Verify if configured category exists in Discord"""
        if not self.category_id:
            logger.warning("No category ID configured")
            return False
            
        try:
            category = self.bot.get_channel(int(self.category_id))
            if category and isinstance(category, CategoryChannel):
                self.category = category
                logger.info(f"Verified category exists: {category.name} (ID: {self.category_id})")
                return True
            else:
                logger.warning(f"Category ID {self.category_id} not found or not a category")
                return False
        except Exception as e:
            logger.error(f"Error verifying category: {e}")
            return False
            
    async def create_category(self) -> Optional[CategoryChannel]:
        """Create a new category for the bot"""
        try:
            logger.info("Creating new Homelab category")
            category_name = "HOMELAB"
            
            # Set up permissions - admin roles can see, others cannot
            overwrites = {
                self.guild.default_role: PermissionOverwrite(read_messages=False),
                self.guild.me: PermissionOverwrite(read_messages=True, manage_channels=True)
            }
            
            # Create the category
            category = await self.guild.create_category(
                name=category_name,
                overwrites=overwrites,
                reason="Homelab Bot initialization"
            )
            
            self.category = category
            self.category_id = category.id
            
            # Store in database
            await self._store_category_mapping(category.id)
            
            logger.info(f"Created new category: {category.name} (ID: {category.id})")
            return category
            
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            return None
    
    async def ensure_category_exists(self) -> Optional[CategoryChannel]:
        """Ensure category exists, creating it if necessary"""
        # First verify if it exists
        exists = await self.verify_category("HOMELAB")
        
        if exists:
            return self.category
            
        # Create new category
        category = await self.create_category()
        if category:
            logger.info(f"Category created/ensured: {category.name}")
            return category
        else:
            logger.error("Failed to create category")
            return None
    
    async def _store_category_mapping(self, category_id):
        """Store category ID mapping in database"""
        try:
            async for session in get_session():
                # Check if mapping exists
                result = await session.execute(select(CategoryMapping).where(
                    CategoryMapping.guild_id == str(self.guild.id)
                ))
                mapping = result.scalars().first()
                
                if mapping:
                    # Update existing mapping
                    await session.execute(
                        update(CategoryMapping)
                        .where(CategoryMapping.guild_id == str(self.guild.id))
                        .values(category_id=str(category_id))
                    )
                else:
                    # Create new mapping
                    new_mapping = CategoryMapping(
                        guild_id=str(self.guild.id),
                        category_id=str(category_id),
                        category_name=self.category.name
                    )
                    session.add(new_mapping)
                    
                await session.commit()
                logger.info(f"Category mapping stored in database: {category_id}")
                
        except Exception as e:
            logger.error(f"Error storing category mapping: {e}")

    async def _verify_category_integrity(self):
        """Verify all categories exist and repair if needed"""
        try:
            from infrastructure.config.category_config import CategoryConfig
            from infrastructure.config.constants.category_constants import CATEGORIES
            
            logger.info("Verifying category integrity...")
            missing_categories = []
            
            # Check each category
            for category_key, category_config in CATEGORIES.items():
                if not await self.verify_category(category_key):
                    missing_categories.append(category_key)
            
            if missing_categories:
                logger.warning(f"Found {len(missing_categories)} missing categories: {missing_categories}")
                
                # Attempt to repair each missing category
                for category_key in missing_categories:
                    repaired = await self.create_category()
                    if repaired:
                        logger.info(f"Successfully created category: {CATEGORIES[category_key]['name']}")
                    else:
                        logger.error(f"Failed to create category: {CATEGORIES[category_key]['name']}")
            else:
                logger.info("All categories are intact")
                
        except Exception as e:
            logger.error(f"Category integrity verification failed: {e}")

    async def initialize_categories(self):
        """Initialize categories that are marked for auto-creation"""
        try:
            # Check for Homelab category
            if os.environ.get('HOMELAB_CATEGORY_ID', 'auto') == 'auto':
                logger.info("Auto-creating Homelab category")
                homelab_category = await self.create_category()
                os.environ['HOMELAB_CATEGORY_ID'] = str(homelab_category.id)
                logger.info(f"Created Homelab category with ID: {homelab_category.id}")
                
                # Store in database
                await self._store_category_mapping(homelab_category.id)
                
            # Check for Gameservers category
            if os.environ.get('GAMESERVERS_CATEGORY_ID', 'auto') == 'auto':
                logger.info("Auto-creating Gameservers category")
                gameservers_category = await self.create_category()
                os.environ['GAMESERVERS_CATEGORY_ID'] = str(gameservers_category.id)
                logger.info(f"Created Gameservers category with ID: {gameservers_category.id}")
                
                # Store in database
                await self._store_category_mapping(gameservers_category.id, category_type="gameservers")
                
        except Exception as e:
            logger.error(f"Error auto-creating categories: {e}")
            raise

    async def create_category(self, name):
        """Create a new category in the Discord server"""
        return await self.guild.create_category(name)
    
    async def _store_category_mapping(self, category_id, category_type="homelab"):
        """Store category ID mapping in database"""
        try:
            async for session in get_session():
                # Check if mapping exists
                result = await session.execute(select(CategoryMapping).where(
                    CategoryMapping.guild_id == str(self.guild.id),
                    CategoryMapping.category_type == category_type
                ))
                mapping = result.scalars().first()
                
                if mapping:
                    # Update existing mapping
                    await session.execute(
                        update(CategoryMapping)
                        .where(CategoryMapping.guild_id == str(self.guild.id),
                               CategoryMapping.category_type == category_type)
                        .values(category_id=str(category_id))
                    )
                else:
                    # Create new mapping
                    new_mapping = CategoryMapping(
                        guild_id=str(self.guild.id),
                        category_id=str(category_id),
                        category_name=self.category.name,
                        category_type=category_type
                    )
                    session.add(new_mapping)
                    
                await session.commit()
                logger.info(f"{category_type.capitalize()} category mapping stored in database: {category_id}")
                
        except Exception as e:
            logger.error(f"Error storing category mapping: {e}")

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