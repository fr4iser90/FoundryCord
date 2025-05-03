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
    register_core_services
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

        setup_core_components(self)
        register_workflows(self)

        self.add_check(check_guild_approval)
        logger.info("Registered global check for guild approval on all commands.")

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")

        # Start workflow initialization
        if await self.start_initialization(self):
            # --- Activate DB Dashboards AFTER workflows are initialized ---
            if self.dashboard_workflow and self.dashboard_workflow.lifecycle_service:
                 logger.info("on_ready: Triggering activation of DB-configured dashboards...")
                 try:
                     await self.dashboard_workflow.lifecycle_service.activate_db_configured_dashboards()
                 except Exception as e:
                      logger.error(f"Error during deferred activation of DB dashboards: {e}", exc_info=True)
            else:
                 logger.warning("on_ready: Cannot activate DB dashboards - DashboardWorkflow or LifecycleService not available.")
            # --- End Activation ---

            # Start the internal API server only if initialization was successful
            if self.internal_api_server:
                await self.internal_api_server.start()
            else:
                 logger.error("Internal API Server not initialized, cannot start.")
        else:
             logger.error("Bot initialization failed, skipping deferred actions.")


    async def start_initialization(self, bot_instance):
        """Start the bot initialization process"""
        logger.info("Starting bot initialization")
        if not self.workflow_manager:
             logger.error("Workflow manager not initialized. Cannot start initialization.")
             return False

        factory_type_before_init = type(getattr(bot_instance, 'service_factory', None)).__name__
        logger.info(f"[DIAGNOSTIC main.start_initialization] BEFORE calling initialize_all: bot_instance.service_factory type is {factory_type_before_init}")

        success = await self.workflow_manager.initialize_all(bot_instance)

        if not success:
            logger.error("Bot initialization failed")
            return False

        logger.info("Bot initialization completed successfully")
        return True

    async def cleanup(self):
        """Clean up all resources before shutdown"""
        logger.info("Cleaning up bot resources")

        if self.internal_api_server:
             await self.internal_api_server.stop()

        if self.workflow_manager:
            await self.workflow_manager.cleanup_all()

        logger.info("Bot resources cleaned up successfully")

    async def setup_hook(self):
        """Setup hook called when bot is starting up"""
        logger.info("Starting bot setup_hook...")

        logger.info("Initializing Service Factory...")
        factory_instance = None
        try:
            logger.debug("[DEBUG bot.py setup_hook] Attempting to instantiate ServiceFactory(self)...")
            factory_instance = ServiceFactory(self)
            instance_type = type(factory_instance).__name__ if factory_instance else 'None'
            logger.debug(f"[DEBUG bot.py setup_hook] ServiceFactory(self) returned instance of type: {instance_type}")
            self.service_factory = factory_instance
            factory_type = type(self.service_factory).__name__ if self.service_factory else 'None'
            bot_id = self.user.id if self.user else 'N/A'
            logger.info(f"[DEBUG bot.py setup_hook] Service Factory assigned. Bot ID: {bot_id}, self.service_factory Type: {factory_type}")
        except Exception as e:
             logger.critical(f"CRITICAL: Failed during Service Factory instantiation or assignment: {e}", exc_info=True)
             self.service_factory = None

        register_default_components(self)
        await register_core_services(self)

        logger.info("Bot setup_hook finished.")


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
