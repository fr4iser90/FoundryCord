import nextcord
import logging
from typing import Dict, List, Optional
import asyncio
from app.shared.domain.repositories.discord.category_repository import CategoryRepository
from app.bot.application.services.category.category_builder import CategoryBuilder
from app.shared.infrastructure.models.discord.entities.category_entity import CategoryEntity
from app.shared.infrastructure.models.discord.enums.category import CategoryPermissionLevel
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.repositories.discord.category_repository_impl import CategoryRepositoryImpl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = get_bot_logger()

class CategorySetupService:
    """Service for setting up Discord categories"""
    
    def __init__(self, category_builder: CategoryBuilder):
        """Initialize the category setup service"""
        self.category_builder = category_builder
    
    async def setup_categories(self, guild: nextcord.Guild, session: AsyncSession) -> Dict[str, nextcord.CategoryChannel]:
        """Set up all categories for the guild"""
        category_repo = CategoryRepositoryImpl(session)
        categories_result = await session.execute(select(CategoryEntity).filter_by(is_enabled=True))
        categories = categories_result.scalars().all()
        
        if not categories:
            logger.warning(f"No enabled categories found in the database for setup")
            return {}
            
        logger.info(f"Setting up {len(categories)} categories for guild {guild.name}")
        
        result = {}
        for category in categories:
            discord_category = await self.setup_category(guild, category, session)
            if discord_category:
                result[category.name] = discord_category
        
        return result
    
    async def setup_category(self, guild: nextcord.Guild, category_model: CategoryEntity, session: AsyncSession) -> Optional[nextcord.CategoryChannel]:
        """Set up a single category in the guild"""
        logger.info(f"Setting up category: {category_model.name}")
        
        category_repo = CategoryRepositoryImpl(session)

        existing_by_id = None
        existing_by_name = None
        
        if category_model.discord_id:
            existing_by_id = nextcord.utils.get(guild.categories, id=category_model.discord_id)
            
        if not existing_by_id:
            existing_by_name = nextcord.utils.get(guild.categories, name=category_model.name)
        
        if existing_by_id:
            logger.info(f"Found existing category with ID {category_model.discord_id}")
            return existing_by_id
            
        elif existing_by_name:
            logger.info(f"Found existing category with name {category_model.name} (ID: {existing_by_name.id})")
            await category_repo.update_discord_id(category_model.id, existing_by_name.id)
            await category_repo.update_category_status(category_model.id, True)
            logger.info(f"Updated category {category_model.name} with Discord ID {existing_by_name.id}")
            return existing_by_name
            
        else:
            logger.info(f"Creating new category: {category_model.name}")
            try:
                discord_category = await self.category_builder.create_category(guild, category_model, session)
                if discord_category:
                    await category_repo.update_discord_id(category_model.id, discord_category.id)
                    await category_repo.update_category_status(category_model.id, True)
                    logger.info(f"Created category {category_model.name} with Discord ID {discord_category.id}")
                    return discord_category
                else:
                    logger.error(f"Failed to create category: {category_model.name}")
                    return None
            except Exception as e:
                logger.error(f"Error creating category {category_model.name}: {str(e)}")
                return None
    
    async def sync_with_discord(self, guild: nextcord.Guild, session: AsyncSession) -> None:
        """Sync categories with existing Discord categories"""
        
        category_repo = CategoryRepositoryImpl(session)
        categories = await category_repo.get_all_categories()
        
        discord_categories = guild.categories
        
        discord_categories_by_name = {c.name: c for c in discord_categories}
        
        for category in categories:
            if category.name in discord_categories_by_name:
                discord_category = discord_categories_by_name[category.name]
                
                if category.discord_id != discord_category.id:
                    logger.info(f"Updating Discord ID for category {category.name} from {category.discord_id} to {discord_category.id}")
                    await category_repo.update_discord_id(category.id, discord_category.id)
                    await category_repo.mark_as_created(category.id)
                    
                if category.position != discord_category.position:
                    logger.info(f"Updating position for category {category.name} from {category.position} to {discord_category.position}")
                    await category_repo.update_position(category.id, discord_category.position)
    
    async def get_category_by_name(self, name: str, session: AsyncSession) -> Optional[CategoryEntity]:
        """
        Get a category model by name from database
        """
        category_repo = CategoryRepositoryImpl(session)
        cat_result = await session.execute(select(CategoryEntity).where(CategoryEntity.name == name))
        category = cat_result.scalars().first()
        return category
    
    async def setup_category(self, guild: nextcord.Guild, category_model: CategoryEntity, session: AsyncSession) -> Optional[nextcord.CategoryChannel]:
        """Set up a single category in the guild"""
        logger.info(f"Setting up category: {category_model.name}")
        
        category_repo = CategoryRepositoryImpl(session)

        existing_by_id = None
        existing_by_name = None
        
        if category_model.discord_id:
            existing_by_id = nextcord.utils.get(guild.categories, id=category_model.discord_id)
            
        if not existing_by_id:
            existing_by_name = nextcord.utils.get(guild.categories, name=category_model.name)
        
        if existing_by_id:
            logger.info(f"Found existing category with ID {category_model.discord_id}")
            return existing_by_id
            
        elif existing_by_name:
            logger.info(f"Found existing category with name {category_model.name} (ID: {existing_by_name.id})")
            await category_repo.update_discord_id(category_model.id, existing_by_name.id)
            await category_repo.update_category_status(category_model.id, True)
            logger.info(f"Updated category {category_model.name} with Discord ID {existing_by_name.id}")
            return existing_by_name
            
        else:
            logger.info(f"Creating new category: {category_model.name}")
            try:
                discord_category = await self.category_builder.create_category(guild, category_model, session)
                if discord_category:
                    await category_repo.update_discord_id(category_model.id, discord_category.id)
                    await category_repo.update_category_status(category_model.id, True)
                    logger.info(f"Created category {category_model.name} with Discord ID {discord_category.id}")
                    return discord_category
                else:
                    logger.error(f"Failed to create category: {category_model.name}")
                    return None
            except Exception as e:
                logger.error(f"Error creating category {category_model.name}: {str(e)}")
                return None 