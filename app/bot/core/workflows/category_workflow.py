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
from app.shared.domain.repositories.discord.category_repository import CategoryRepository
from app.shared.infrastructure.repositories.discord import CategoryRepositoryImpl

logger = get_bot_logger()

class CategoryWorkflow(BaseWorkflow):
    """Workflow for category setup and management"""
    
    def __init__(self, database_workflow: DatabaseWorkflow, bot):
        super().__init__("category")
        self.database_workflow = database_workflow
        self.bot = bot
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
            # --- REMOVED OLD DB CHECK ---
            # Verify categories exist using direct SQL instead of ORM to avoid mapping issues
            # async with session_context() as session:
            #     # Use direct SQL query to check if the table exists and has data
            #     try:
            #         result = await session.execute(text("SELECT COUNT(*) FROM discord_categories"))
            #         count = result.scalar()
            #         logger.info(f"Found {count} categories")
            #         if count == 0:
            #             logger.warning("Table 'discord_categories' exists but is empty. Continuing initialization.")
            #             # If the table is empty, maybe it's okay to proceed in the new template world?
            #             # Or should we still error? For now, let's proceed.
            #     except Exception as db_err:
            #         # Catch specific error if table doesn't exist
            #         if "relation \"discord_categories\" does not exist" in str(db_err):
            #             logger.warning("'discord_categories' table does not exist (expected during refactoring). Continuing initialization.")
            #             # This is now expected, so we continue
            #         else:
            #             logger.error(f"Unexpected database error checking discord_categories: {db_err}")
            #             return False # Propagate unexpected errors

            # Initialize components needed later, but don't load old data
            async with session_context() as session:
                # Still create the repository implementation
                self.category_repository = CategoryRepositoryImpl(session)
                logger.debug("CategoryRepositoryImpl initialized.")

                # Create a simplified builder and service (if needed by other components)
                # These might need further refactoring if they still rely on old structures.
                category_builder = CategoryBuilder(self.category_repository)
                self.category_setup_service = CategorySetupService(
                    self.category_repository,
                    category_builder
                )
                # Initialize cache as empty
                self.category_setup_service.categories_cache = {}
                logger.debug("CategorySetupService initialized with empty cache.")

                # Maintain backwards compatibility if needed
                self.category_service = self.category_setup_service

            logger.info("Category workflow initialized globally (skipping old data load).")
            return True

        except Exception as e:
            logger.error(f"Error initializing category workflow: {e}", exc_info=True)
            # traceback.print_exc() # Handled by exc_info=True
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
            
            # --- Temporarily Disable Old Logic --- 
            logger.warning(f"CategoryWorkflow.initialize_for_guild: Old setup/sync logic for guild {guild_id} is disabled. Structure now comes from templates.")
            # # Set up categories (OLD LOGIC - accesses discord_categories)
            # categories = await self.setup_categories(guild)
            # if not categories:
            #     logger.error(f"Failed to set up categories for guild {guild_id}")
            #     self.guild_status[guild_id] = WorkflowStatus.FAILED
            #     return False
                
            # # Sync with Discord (OLD LOGIC)
            # await self.sync_with_discord(guild)
            # --- End Disable --- 
            
            # Mark as active (conceptually, it's ready if guild is approved)
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
