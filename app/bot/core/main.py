# @/app/bot/core/main.py
import os
import logging
import asyncio
import nextcord
from nextcord.ext import commands
import sys
from typing import Dict, Any, Optional, List

from app.shared.interface.logging.api import get_bot_logger
from app.bot.core.setup_hooks import (
    setup_core_components,
    register_workflows,
    register_default_components,
    setup_service_factory_and_register_core_services,
    setup_hook
)
from app.bot.infrastructure.factories.service_factory import ServiceFactory
from app.bot.core.checks import check_guild_approval


logger = get_bot_logger()

# Suppress nextcord gateway logs
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

        # Initialize service_factory as None *before* setup calls
        self.service_factory: Optional[ServiceFactory] = None

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
        logger.info("Registered global check for guild approval on all commands.")

        # Example: Initialize Internal API Server (if it needs services)
        if self.internal_api_server and self.service_factory:
             # Re-initialize or pass factory if needed.
             # Assuming InternalAPIServer's constructor takes bot, and can access bot.service_factory
             logger.info("Internal API Server setup linked with Service Factory.")
        elif not self.internal_api_server:
             logger.warning("Internal API Server component not setup.")
        else: # Service factory failed
             logger.error("Cannot finish Internal API Server setup - Service Factory failed to initialize.")


        logger.info("FoundryCord __init__ complete.")


    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")

        # --- Start workflow and service initialization ---
        initialization_success = False
        try:
            initialization_success = await self.start_initialization(self) # Pass self
        except Exception as init_err:
             logger.critical(f"An uncaught exception occurred during start_initialization: {init_err}", exc_info=True)
             initialization_success = False # Ensure it's marked as failed

        if initialization_success:
            logger.info("Core initialization (Workflows & Services) completed successfully.")
            # --- ADD DELAY (Keep commented out for now, re-enable if needed) ---
            # wait_seconds = 5 # Wait 5 seconds
            # logger.info(f"Waiting {wait_seconds}s before activating DB dashboards...")
            # await asyncio.sleep(wait_seconds)
            # logger.info("Wait finished. Proceeding with DB dashboard activation.")
            # --- END DELAY ---

            # --- Activate DB Dashboards AFTER workflows AND services are initialized ---
            if hasattr(self, 'dashboard_workflow') and self.dashboard_workflow and hasattr(self.dashboard_workflow, 'lifecycle_service') and self.dashboard_workflow.lifecycle_service:
                 logger.info("on_ready: Triggering activation of DB-configured dashboards...")
                 try:
                     # This call now happens after services (like ComponentRegistry) are initialized
                     await self.dashboard_workflow.lifecycle_service.activate_db_configured_dashboards()
                 except Exception as e:
                      logger.error(f"Error during deferred activation of DB dashboards: {e}", exc_info=True)
            else:
                 logger.warning("on_ready: Cannot activate DB dashboards - DashboardWorkflow or LifecycleService not available/initialized.")
            # --- End Activation ---

            # Start the internal API server only if initialization was successful
            if self.internal_api_server:
                await self.internal_api_server.start()
            else:
                 logger.error("Internal API Server not initialized or failed to start.")
        else:
             logger.error("Bot core initialization (Workflows/Services) failed. Skipping deferred actions and API start.")


    async def start_initialization(self, bot_instance):
        """Initializes workflows and then core services."""
        logger.info("Starting bot core initialization...")

        # 1. Initialize Workflows
        logger.info("Initializing workflows...")
        if not self.workflow_manager:
             logger.error("Workflow manager not initialized. Cannot start initialization.")
             return False
        if not bot_instance.service_factory:
             logger.critical("CRITICAL ERROR: bot_instance.service_factory is None before workflow initialization!")
             return False

        workflow_success = await self.workflow_manager.initialize_all(bot_instance)
        if not workflow_success:
            logger.error("Workflow initialization failed.")
            return False
        logger.info("Workflow initialization completed successfully.")

        # 2. Initialize Services (after workflows)
        logger.info("Initializing core services via ServiceFactory...")
        service_init_success = False
        try:
            # Call initialize_services on the factory instance
            service_init_success = await bot_instance.service_factory.initialize_services()
            if not service_init_success:
                 logger.error("Core service initialization failed (returned False).")
                 # Decide if this is critical. For now, let's say it is.
                 return False
            else:
                 logger.info("Core service initialization completed successfully.")
        except Exception as service_err:
            logger.error(f"An exception occurred during service initialization: {service_err}", exc_info=True)
            return False # Treat exceptions during service init as critical failure

        logger.info("Bot core initialization completed successfully.")
        return True # Return True only if both workflow and service init succeed

    async def cleanup(self):
        """Clean up all resources before shutdown"""
        logger.info("Cleaning up bot resources")

        if self.internal_api_server:
             await self.internal_api_server.stop()

        if self.workflow_manager:
            await self.workflow_manager.cleanup_all()

        logger.info("Bot resources cleaned up successfully")

    async def setup_hook(self):
        """Setup hook called when bot is starting up. ServiceFactory moved to __init__."""
        # Call the (now mostly empty regarding factory) setup_hook from setup_hooks.py
        await setup_hook(self)
        logger.info("Bot setup_hook finished (Factory init moved).")


async def main():
    """Main entry point for the bot"""
    try:
        intents = nextcord.Intents.default()
        intents.members = True
        intents.message_content = True

        bot = FoundryCord(command_prefix="!", intents=intents)

        logger.info("Starting the bot...")
        await bot.start(os.getenv('DISCORD_BOT_TOKEN'))

    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
