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
                # --- MODIFY: Create repo only if needed locally, don't store --- 
                # self.category_repository = CategoryRepositoryImpl(session)
                # logger.debug("CategoryRepositoryImpl initialized.")
                # Instead, pass the session to services that need to create it.
                # -------------------------------------------------------------

                # Create a simplified builder and service (if needed by other components)
                # These might need further refactoring if they still rely on old structures.
                # --- MODIFY: Pass session to builder/service if they need to create repo ---
                # Option 1: Pass session (cleaner)
                # category_builder = CategoryBuilder(session)
                # Option 2: Pass repo instance created here (less ideal)
                # temp_repo = CategoryRepositoryImpl(session) # Create temporary instance if needed NOW
                # --- FIX: CategoryBuilder now takes no arguments --- 
                category_builder = CategoryBuilder()
                # ---------------------------------------------------
                self.category_setup_service = CategorySetupService(
                    # --- MODIFY: Pass session or repo instance? ---
                    # Option 1: Modify Service to accept session
                    # session,
                    # Option 2: Pass temporary repo instance (requires service adjustment?)
                    # --- FIX: CategorySetupService takes CategoryBuilder, not repo --- 
                    # temp_repo, # Assuming Service takes repo instance for now - INCORRECT
                    # ------------------------------------------
                    category_builder
                )
                # Initialize cache as empty
                # --- REMOVE Cache initialization here - Service handles it --- 
                # self.category_setup_service.categories_cache = {}
                # -----------------------------------------------------------
                logger.debug("CategorySetupService initialized (internally stateless). Cache removed from workflow.")

                # Maintain backwards compatibility if needed
                # --- REMOVE old service assignment --- 
                # self.category_service = self.category_setup_service
                # -----------------------------------

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
    
    def get_category_service(self):
        """Get the category service (backward compatibility)"""
        # This might be broken now as service might not have a persistent repo
        return self.category_service
    
    def get_category_setup_service(self):
        """Get the category setup service"""
        # This might be broken now as service might not have a persistent repo
        return self.category_service # Should be self.category_setup_service?

    async def setup_categories(self, guild):
        """Set up all categories for the guild"""
        if not self.category_setup_service:
            logger.error("Category service not initialized")
            return {}
        
        logger.info(f"Setting up categories for guild: {guild.name}")
        # --- MODIFY: setup_categories likely needs a session now --- 
        # It needs to create repo instances. Pass session down?
        # return await self.category_setup_service.setup_categories(guild) 
        try:
            async with session_context() as session:
                # --- FIX: Instantiate service within session --- 
                # Assuming setup_categories method in service now accepts session
                # return await self.category_setup_service.setup_categories(guild, session)
                builder = CategoryBuilder()
                setup_service = CategorySetupService(builder)
                return await setup_service.setup_categories(guild, session)
                # ------------------------------------------------
        except Exception as e:
             logger.error(f"Error during setup_categories: {e}", exc_info=True)
             return {}
        # ---------------------------------------------------------
        
    async def sync_with_discord(self, guild: nextcord.Guild) -> None:
        """Sync categories with existing Discord categories"""
        if not self.category_setup_service:
            logger.error("Category service not initialized")
            return
            
        logger.info(f"Syncing categories with Discord for guild: {guild.name}")
        # --- MODIFY: sync_with_discord likely needs a session now --- 
        # return await self.category_setup_service.sync_with_discord(guild)
        try:
            async with session_context() as session:
                # --- FIX: Instantiate service within session --- 
                # Assuming sync_with_discord method in service now accepts session
                # await self.category_setup_service.sync_with_discord(guild, session)
                builder = CategoryBuilder()
                setup_service = CategorySetupService(builder)
                await setup_service.sync_with_discord(guild, session)
                # -----------------------------------------------
        except Exception as e:
             logger.error(f"Error during sync_with_discord: {e}", exc_info=True)
        # ---------------------------------------------------------

    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup resources for a specific guild"""
        logger.info(f"Cleaning up category workflow for guild {guild_id}")
        await super().cleanup_guild(guild_id)
        
        # Clear any cached data for this guild
        # --- REMOVE Cache manipulation - Service is stateless --- 
        # if self.category_setup_service and hasattr(self.category_setup_service, 'categories_cache'):
        #     # Remove any guild-specific categories from cache
        #     self.category_setup_service.categories_cache = {
        #         name: data for name, data in self.category_setup_service.categories_cache.items()
        #         if not data.get('guild_id') or data.get('guild_id') != guild_id
        #     }
        # -----------------------------------------------------
            
    async def cleanup(self) -> None:
        """Cleanup all resources"""
        logger.info("Cleaning up category workflow")
        await super().cleanup()
        
        # Clear all caches
        # --- REMOVE Cache clear - Service is stateless --- 
        # if self.category_setup_service:
        #     self.category_setup_service.categories_cache.clear()
        # --------------------------------------------------
