import logging
import nextcord
import asyncio
from typing import Dict, Optional, List
from sqlalchemy import text
import traceback

from app.bot.core.workflows.base_workflow import BaseWorkflow, WorkflowStatus
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.session.context import session_context
from app.bot.application.services.category.category_setup_service import CategorySetupService
from app.bot.application.services.category.category_builder import CategoryBuilder
from app.bot.domain.categories.repositories.category_repository import CategoryRepository
from app.shared.infrastructure.repositories.discord import CategoryRepositoryImpl

logger = get_bot_logger()

class CategoryWorkflow(BaseWorkflow):
    """Workflow for category setup and management"""
    
    def __init__(self, database_workflow: DatabaseWorkflow):
        super().__init__("category")
        self.database_workflow = database_workflow
        self.category_repository = None
        self.category_service = None
        self.category_setup_service = None
        
        # Define dependencies
        self.add_dependency("database")
        
        # Categories require guild approval
        self.requires_guild_approval = True
    
    async def initialize(self) -> bool:
        """Initialize the category workflow globally"""
        try:
            # Verify categories exist using direct SQL instead of ORM to avoid mapping issues
            async with session_context() as session:
                # Use direct SQL query to check if the table exists and has data
                result = await session.execute(text("SELECT COUNT(*) FROM discord_categories"))
                count = result.scalar()
                
                if count == 0:
                    logger.error("No categories found. Please run database migrations first")
                    return False
                
                logger.info(f"Found {count} categories")
                
                # Create a clean session for repository
                self.category_repository = CategoryRepositoryImpl(session)
                
                # For category_builder, create a simplified version that doesn't rely on ORM
                try:
                    category_builder = CategoryBuilder(self.category_repository)
                    self.category_setup_service = CategorySetupService(
                        self.category_repository,
                        category_builder
                    )
                    
                    # Initialize with a simplified approach that avoids ORM relationship issues
                    self.category_setup_service.categories_cache = {}
                    
                    # Just load the basic category data using direct SQL with correct column names
                    categories_query = text("SELECT id, name, position, description, is_private, created_at FROM discord_categories")
                    categories_result = await session.execute(categories_query)
                    
                    # Manually create category objects for cache
                    for row in categories_result:
                        id, name, position, description, is_private, created_at = row
                        category = {
                            "id": id, 
                            "name": name,
                            "position": position,
                            "description": description,
                            "is_private": is_private,
                            "created_at": created_at,
                            # Provide default values for expected properties that don't exist in DB
                            "discord_id": None,
                            "category_type": "default",
                            "guild_id": None,
                            "enabled": True,
                            "created": True
                        }
                        self.category_setup_service.categories_cache[name] = category
                    
                    logger.info(f"Loaded {len(self.category_setup_service.categories_cache)} categories into cache")
                    
                    # Maintain backwards compatibility with existing code
                    self.category_service = self.category_setup_service
                    
                    return True
                    
                except Exception as inner_e:
                    logger.error(f"Error initializing category service: {inner_e}")
                    traceback.print_exc()
                    return False
                
        except Exception as e:
            logger.error(f"Error initializing category workflow: {e}")
            traceback.print_exc()
            return False
            
    async def initialize_for_guild(self, guild_id: str) -> bool:
        """Initialize workflow for a specific guild"""
        try:
            # Update status to initializing
            self.guild_status[guild_id] = WorkflowStatus.INITIALIZING
            
            # Get the guild
            if not hasattr(self, 'bot') or not self.bot:
                logger.error("Bot instance not available")
                self.guild_status[guild_id] = WorkflowStatus.FAILED
                return False
                
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id}")
                self.guild_status[guild_id] = WorkflowStatus.FAILED
                return False
            
            # Set up categories
            categories = await self.setup_categories(guild)
            if not categories:
                logger.error(f"Failed to set up categories for guild {guild_id}")
                self.guild_status[guild_id] = WorkflowStatus.FAILED
                return False
                
            # Sync with Discord
            await self.sync_with_discord(guild)
            
            # Mark as active
            self.guild_status[guild_id] = WorkflowStatus.ACTIVE
            return True
            
        except Exception as e:
            logger.error(f"Error initializing category workflow for guild {guild_id}: {e}")
            self.guild_status[guild_id] = WorkflowStatus.FAILED
            return False
    
    def get_category_repository(self):
        """Get the category repository"""
        return self.category_repository
    
    def get_category_service(self):
        """Get the category service (backward compatibility)"""
        return self.category_service
    
    def get_category_setup_service(self):
        """Get the category setup service"""
        return self.category_service

    async def setup_categories(self, guild):
        """Set up all categories for the guild"""
        if not self.category_setup_service:
            logger.error("Category service not initialized")
            return {}
        
        logger.info(f"Setting up categories for guild: {guild.name}")
        return await self.category_setup_service.setup_categories(guild)
        
    async def sync_with_discord(self, guild: nextcord.Guild) -> None:
        """Sync categories with existing Discord categories"""
        if not self.category_setup_service:
            logger.error("Category service not initialized")
            return
            
        logger.info(f"Syncing categories with Discord for guild: {guild.name}")
        await self.category_setup_service.sync_with_discord(guild)
        
    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup resources for a specific guild"""
        logger.info(f"Cleaning up category workflow for guild {guild_id}")
        await super().cleanup_guild(guild_id)
        
        # Clear any cached data for this guild
        if self.category_setup_service and hasattr(self.category_setup_service, 'categories_cache'):
            # Remove any guild-specific categories from cache
            self.category_setup_service.categories_cache = {
                name: data for name, data in self.category_setup_service.categories_cache.items()
                if not data.get('guild_id') or data.get('guild_id') != guild_id
            }
            
    async def cleanup(self) -> None:
        """Cleanup all resources"""
        logger.info("Cleaning up category workflow")
        await super().cleanup()
        
        # Clear all caches
        if self.category_setup_service:
            self.category_setup_service.categories_cache.clear()
