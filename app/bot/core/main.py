# @/app/bot/core/main.py
import os
import logging
import asyncio
import nextcord
from nextcord.ext import commands
import sys
from typing import Dict, Any, Optional, List
from app.shared.interface.logging.api import get_bot_logger
from app.bot.core.lifecycle_manager import BotLifecycleManager
from app.bot.core.shutdown_handler import ShutdownHandler
from app.bot.core.workflow_manager import BotWorkflowManager
from app.bot.core.workflows import (
    DatabaseWorkflow,
    GuildWorkflow,
    CategoryWorkflow,
    ChannelWorkflow,
    DashboardWorkflow,
    TaskWorkflow,
    UserWorkflow
)
# Import the new workflow
from app.bot.core.workflows.guild_template_workflow import GuildTemplateWorkflow
# Import the new service
from app.bot.application.services.bot_control_service import BotControlService
# Import the Internal API Server
from app.bot.infrastructure.internal_api.server import InternalAPIServer
# Import the check function
from app.bot.core.checks import check_guild_approval
from app.bot.application.services.dashboard.component_loader_service import ComponentLoaderService
from app.bot.infrastructure.factories.service_factory import ServiceFactory
from app.bot.infrastructure.factories.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.component_factory import ComponentFactory
from app.bot.interfaces.dashboards.components.common.embeds.dashboard_embed import DashboardEmbed
from app.bot.interfaces.dashboards.components.common.embeds.error_embed import ErrorEmbed

logger = get_bot_logger()

# Suppress nextcord gateway logs by setting them to WARNING level only
logging.getLogger("nextcord.gateway").setLevel(logging.WARNING)
logging.getLogger("nextcord.client").setLevel(logging.WARNING)
logging.getLogger("nextcord.http").setLevel(logging.WARNING)

class FoundryCord(commands.Bot):
    """Main bot class for the Homelab Discord Bot"""
    
    def __init__(self, command_prefix="!", intents=None):
        if intents is None:
            intents = nextcord.Intents.default()
            intents.members = True
            intents.message_content = True
        
        super().__init__(command_prefix=command_prefix, intents=intents)
        
        # Initialize managers
        self.lifecycle = BotLifecycleManager()
        self.workflow_manager = BotWorkflowManager()
        
        # --- ADD Component Registry/Factory from interfaces/bot.py ---
        logger.info("Initializing component registry and factory in constructor")
        self.component_registry = ComponentRegistry()
        self.component_factory = ComponentFactory(self.component_registry)
        # Initialize service_factory attribute to None initially
        self.service_factory = None
        self._default_components_registered = False
        # --- END ADD ---
        
        # Create all workflow instances
        self.database_workflow = DatabaseWorkflow(self)
        self.guild_workflow = GuildWorkflow(self.database_workflow, bot=self)
        self.category_workflow = CategoryWorkflow(self.database_workflow, bot=self)
        self.channel_workflow = ChannelWorkflow(self.database_workflow, self.category_workflow, bot=self)
        self.dashboard_workflow = DashboardWorkflow(self.database_workflow)
        self.task_workflow = TaskWorkflow(self.database_workflow, self)
        self.user_workflow = UserWorkflow(self.database_workflow, self)
        # Instantiate the new workflow
        self.guild_template_workflow = GuildTemplateWorkflow(self.database_workflow, self.guild_workflow, self)
        
        # Register workflows with dependencies
        self.workflow_manager.register_workflow(self.database_workflow)
        self.workflow_manager.register_workflow(self.guild_workflow, ['database'])
        self.workflow_manager.register_workflow(self.guild_template_workflow, ['database', 'guild'])
        self.workflow_manager.register_workflow(self.category_workflow, ['database'])
        self.workflow_manager.register_workflow(self.channel_workflow, ['database', 'category'])
        self.workflow_manager.register_workflow(self.dashboard_workflow, ['database'])
        self.workflow_manager.register_workflow(self.task_workflow, ['database'])
        self.workflow_manager.register_workflow(self.user_workflow, ['database'])
        
        # Set explicit initialization order
        self.workflow_manager.set_initialization_order([
            'database', 
            'guild', 
            'guild_template', # Add to order
            'category', 
            'channel', 
            'dashboard', 
            'task', 
            'user'
        ])
        
        # Add shutdown handler
        self.shutdown_handler = ShutdownHandler(self)

        # --- Initialize BotControlService --- 
        self.control_service = BotControlService(self)
        logger.info("BotControlService attached to bot instance.")
        # --- End Service Init --- 

        # --- Initialize Internal API Server ---
        self.internal_api_server = InternalAPIServer(self)
        logger.info("InternalAPIServer initialized.")
        # --- End Internal API Init ---

        # --- Register Global Check --- 
        # Ensure any previous add_check calls referencing methods are removed
        self.add_check(check_guild_approval) # Use the imported function
        logger.info("Registered global check for guild approval on all commands.")
        # --- End Global Check --- 
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")
        
        # Start initialization
        if await self.start_initialization(self):
            # Start the internal API server only if initialization was successful
            await self.internal_api_server.start()
    
    async def start_initialization(self, bot_instance):
        """Start the bot initialization process"""
        logger.info("Starting bot initialization")
        
        # Initialize all workflows using the workflow manager
        success = await self.workflow_manager.initialize_all(bot_instance)
        
        if not success:
            logger.error("Bot initialization failed")
            return False
            
        logger.info("Bot initialization completed successfully")
        return True

    async def cleanup(self):
        """Clean up all resources before shutdown"""
        logger.info("Cleaning up bot resources")
        
        # Stop the internal API server first
        await self.internal_api_server.stop()
        
        # Use the workflow manager to cleanup all workflows in reverse order
        await self.workflow_manager.cleanup_all()
        
        logger.info("Bot resources cleaned up successfully")

    async def setup_hook(self):
        """Setup hook called when bot is starting up"""
        logger.info("Starting bot setup_hook...")

        # --- ADD SERVICE FACTORY INITIALIZATION HERE ---
        logger.info("Initializing Service Factory...")
        factory_instance = None # Initialize to None
        try:
            # --- ADD DEBUG LOG BEFORE ASSIGNMENT ---
            logger.debug("[DEBUG bot.py setup_hook] Attempting to instantiate ServiceFactory(self)...")
            factory_instance = ServiceFactory(self)
            instance_type = type(factory_instance).__name__ if factory_instance else 'None'
            logger.debug(f"[DEBUG bot.py setup_hook] ServiceFactory(self) returned instance of type: {instance_type}")
            # --- END DEBUG LOG ---

            self.service_factory = factory_instance # Assign the potentially None instance
            
            # Log after assignment
            factory_type = type(self.service_factory).__name__ if self.service_factory else 'None'
            bot_id = self.user.id if self.user else 'N/A'
            logger.info(f"[DEBUG bot.py setup_hook] Service Factory assigned. Bot ID: {bot_id}, self.service_factory Type: {factory_type}")
        except Exception as e:
             logger.critical(f"CRITICAL: Failed during Service Factory instantiation or assignment: {e}", exc_info=True)
             self.service_factory = None # Ensure it's None on error
        # ---------------------------------------------

        # Register default components (moved from init potentially)
        if not self._default_components_registered:
            self.register_default_components()

        # Check if service_factory exists AND IS NOT NONE before using it
        if self.service_factory:
            try:
                self.component_loader = ComponentLoaderService(self) # Pass self (the bot)
                if hasattr(self.service_factory, 'register_service') and hasattr(self.service_factory, 'has_service'):
                    if not self.service_factory.has_service('component_loader'):
                        self.service_factory.register_service(
                            'component_loader',
                            self.component_loader
                        )
                        logger.info("ComponentLoaderService registered with ServiceFactory.")
                else:
                    logger.error("Service Factory instance does not have expected registration methods.")
            except Exception as e:
                logger.error(f"Error initializing or registering ComponentLoaderService: {e}", exc_info=True)
        else:
            # Log why component_loader is not registered
            if factory_instance is None and hasattr(self, 'service_factory') and self.service_factory is None:
                 logger.error("Service Factory is None after instantiation attempt. Cannot register ComponentLoaderService.")
            else:
                 logger.error("Service Factory attribute not available. Cannot register ComponentLoaderService.")

        logger.info("Bot setup_hook finished.")

    def register_default_components(self):
        """Register the default UI components"""
        try:
            # CORE EMBED COMPONENTS
            self.component_registry.register_component(
                component_type="dashboard_embed",
                component_class=DashboardEmbed,
                description="Standard dashboard embed",
                default_config={
                    "title": "Dashboard",
                    "color": nextcord.Color.blurple().value,
                    "timestamp": True
                }
            )
            self.component_registry.register_component(
                component_type="error_embed",
                component_class=ErrorEmbed,
                description="Embed for displaying errors",
                default_config={
                    "title": "Error",
                    "description": "An error occurred",
                    "color": nextcord.Color.red().value,
                    "error_code": None
                }
            )
            self._default_components_registered = True
            logger.info(f"Registered {len(self.component_registry.get_all_component_types())} default components")
        except Exception as e:
            logger.error(f"Error registering default components: {str(e)}")

async def main():
    """Main entry point for the bot"""
    try:
        # Set up intents
        intents = nextcord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        # Create the bot
        bot = FoundryCord(command_prefix="!", intents=intents)
        
        # Run the bot
        logger.info("Starting the bot...")
        await bot.start(os.getenv('DISCORD_BOT_TOKEN'))
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
