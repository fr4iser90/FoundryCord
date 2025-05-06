import logging
import nextcord
from nextcord.ext import commands
import sys
from typing import Dict, Any, Optional, List

# Import necessary components used within FoundryCord
from app.shared.interfaces.logging.api import get_bot_logger
from .setup_hooks import (
    setup_core_components, register_workflows, 
    setup_service_factory_and_register_core_services, register_default_components, 
    setup_hook
)
from app.bot.interfaces.commands.checks import check_guild_approval
from app.bot.application.interfaces.bot import Bot as BotInterface
from app.bot.application.interfaces.service_factory import ServiceFactory as ServiceFactoryInterface

logger = get_bot_logger()

# Suppress nextcord gateway logs (moved from main.py)
logging.getLogger("nextcord.gateway").setLevel(logging.WARNING)
logging.getLogger("nextcord.client").setLevel(logging.WARNING)
logging.getLogger("nextcord.http").setLevel(logging.WARNING)

class FoundryCord(commands.Bot, BotInterface):
    """Main bot class for the Homelab Discord Bot"""

    def __init__(self, command_prefix="!", intents=None):
        if intents is None:
            intents = nextcord.Intents.default()
            intents.members = True
            intents.message_content = True

        super().__init__(command_prefix=command_prefix, intents=intents)

        # Initialize service_factory as None *before* setup calls
        self._service_factory_instance = None

        # Setup components that DON'T depend on service factory first
        setup_core_components(self)
        register_workflows(self)

        # --- MOVED FROM setup_hook / Placed after core components ---
        # Create Factory, Register Core Services, and Register Default Components SYNCHRONOUSLY
        try:
            setup_service_factory_and_register_core_services(self)
            # Register default components AFTER factory and core services exist
            register_default_components(self)
        except Exception as e:
             # If setup fails critically, log and potentially exit or prevent startup
             logger.critical(f"FATAL: Failed essential setup in __init__: {e}. Bot may not function.", exc_info=True)
             # Depending on severity, you might want sys.exit(1) here
             # For now, let it continue but log the critical failure.

        # Now that service factory likely exists, setup things depending on it
        # Example: Setup global check (if it needs services)
        self.add_check(check_guild_approval) # Assuming this check might use services later
        logger.debug("Registered global check for guild approval on all commands.")

        # Example: Initialize Internal API Server (if it needs services)
        if hasattr(self, 'internal_api_server') and self.internal_api_server and self.service_factory:
             # Re-initialize or pass factory if needed.
             # Assuming InternalAPIServer's constructor takes bot, and can access bot.service_factory
             logger.debug("Internal API Server setup linked with Service Factory.")
        elif not hasattr(self, 'internal_api_server'):
             logger.warning("Internal API Server component not setup.")
        else: # Service factory failed
             logger.error("Cannot finish Internal API Server setup - Service Factory failed to initialize.")

        logger.debug("FoundryCord __init__ complete.")

    @property
    def service_factory(self):
        # This property will now return the interface type, 
        # but internally it refers to the concrete _service_factory_instance
        return self._service_factory_instance
    
    # service_factory setter if direct assignment is needed post-init, 
    # though it's set by setup_service_factory_and_register_core_services
    @service_factory.setter
    def service_factory(self, value):
        self._service_factory_instance = value

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f"Bot logged in as {self.user.name} (ID: {self.user.id})")

        # --- Start workflow and service initialization ---
        initialization_success = False
        try:
            initialization_success = await self.start_initialization(self) # Pass self
        except Exception as init_err:
             logger.critical(f"An uncaught exception occurred during start_initialization: {init_err}", exc_info=True)
             initialization_success = False # Ensure it's marked as failed

        if initialization_success:
            logger.debug("Core initialization (Workflows & Services) completed successfully.")
            # --- Activate DB Dashboards AFTER workflows AND services are initialized ---
            if hasattr(self, 'dashboard_workflow') and self.dashboard_workflow and hasattr(self.dashboard_workflow, 'lifecycle_service') and self.dashboard_workflow.lifecycle_service:
                 logger.debug("on_ready: Triggering activation of DB-configured dashboards...")
                 try:
                     # This call now happens after services (like ComponentRegistry) are initialized
                     await self.dashboard_workflow.lifecycle_service.activate_db_configured_dashboards()
                 except Exception as e:
                      logger.error(f"Error during deferred activation of DB dashboards: {e}", exc_info=True)
            else:
                 logger.warning("on_ready: Cannot activate DB dashboards - DashboardWorkflow or LifecycleService not available/initialized.")
            # --- End Activation ---

            # Start the internal API server only if initialization was successful
            if hasattr(self, 'internal_api_server') and self.internal_api_server:
                await self.internal_api_server.start()
            else:
                 logger.error("Internal API Server not initialized or failed to start.")
        else:
             logger.error("Bot core initialization (Workflows/Services) failed. Skipping deferred actions and API start.")


    async def start_initialization(self, bot_instance):
        """Initializes workflows and then core services."""
        logger.debug("Starting bot core initialization...")

        # 1. Initialize Workflows
        logger.debug("Initializing workflows...")
        if not hasattr(self, 'workflow_manager') or not self.workflow_manager:
             logger.error("Workflow manager not initialized. Cannot start initialization.")
             return False
        if not bot_instance.service_factory:
             logger.critical("CRITICAL ERROR: bot_instance.service_factory is None before workflow initialization!")
             return False

        workflow_success = await self.workflow_manager.initialize_all(bot_instance)
        if not workflow_success:
            logger.error("Workflow initialization failed.")
            return False
        logger.debug("Workflow initialization completed successfully.")

        # 2. Initialize Services (after workflows)
        logger.debug("Initializing core services via ServiceFactory...")
        service_init_success = False
        try:
            # Call initialize_services on the factory instance
            service_init_success = await bot_instance.service_factory.initialize_services()
            if not service_init_success:
                 logger.error("Core service initialization failed (returned False).")
                 # Decide if this is critical. For now, let's say it is.
                 return False
            else:
                 logger.debug("Core service initialization completed successfully.")
        except Exception as service_err:
            logger.error(f"An exception occurred during service initialization: {service_err}", exc_info=True)
            return False # Treat exceptions during service init as critical failure

        logger.debug("Bot core initialization completed successfully.")
        return True # Return True only if both workflow and service init succeed

    async def cleanup(self):
        """Clean up all resources before shutdown"""
        logger.info("Cleaning up bot resources")

        if hasattr(self, 'internal_api_server') and self.internal_api_server:
             await self.internal_api_server.stop()

        if hasattr(self, 'workflow_manager') and self.workflow_manager:
            await self.workflow_manager.cleanup_all()

        logger.info("Bot resources cleaned up successfully")

    async def setup_hook(self):
        """Setup hook called when bot is starting up. ServiceFactory moved to __init__."""
        # Call the (now mostly empty regarding factory) setup_hook from setup_hooks.py
        await setup_hook(self)
        logger.info("Bot setup_hook finished (Factory init moved).") 