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

logger = get_bot_logger()

# Suppress nextcord gateway logs by setting them to WARNING level only
logging.getLogger("nextcord.gateway").setLevel(logging.WARNING)
logging.getLogger("nextcord.client").setLevel(logging.WARNING)
logging.getLogger("nextcord.http").setLevel(logging.WARNING)

class HomelabBot(commands.Bot):
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
        
        # Create all workflow instances
        self.database_workflow = DatabaseWorkflow(self)
        self.guild_workflow = GuildWorkflow(self.database_workflow, bot=self)
        self.category_workflow = CategoryWorkflow(self.database_workflow, bot=self)
        self.channel_workflow = ChannelWorkflow(self.database_workflow, self.category_workflow, bot=self)
        self.dashboard_workflow = DashboardWorkflow(self.database_workflow, bot=self)
        self.task_workflow = TaskWorkflow(self.database_workflow, self)
        self.user_workflow = UserWorkflow(self.database_workflow, self)
        # Instantiate the new workflow
        self.guild_template_workflow = GuildTemplateWorkflow(self.database_workflow, self.guild_workflow, self)
        
        # Register workflows with dependencies
        self.workflow_manager.register_workflow(self.database_workflow)
        self.workflow_manager.register_workflow(self.guild_workflow, ['database'])
        # Register the new workflow
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
        # Pass self (the bot instance) to the service
        self.control_service = BotControlService(self)
        logger.info("BotControlService attached to bot instance.")
        # --- End Service Init --- 

        # --- Initialize Internal API Server ---
        self.internal_api_server = InternalAPIServer(self)
        logger.info("InternalAPIServer initialized.")
        # --- End Internal API Init ---
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")
        
        # Start initialization
        if await self.start_initialization():
            # Start the internal API server only if initialization was successful
            await self.internal_api_server.start()
    
    async def start_initialization(self):
        """Start the bot initialization process"""
        logger.info("Starting bot initialization")
        
        # Initialize all workflows using the workflow manager
        success = await self.workflow_manager.initialize_all()
        
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
        """Setup hook that runs before the bot starts"""
        # Now initialize BotControlService properly here or in __init__
        # self.control_service = BotControlService(self) # Already done in __init__
        
        # REMOVED: BotConnector registration is no longer needed here
        # from app.shared.infrastructure.integration.OLD import BotConnector
        # bot_connector = BotConnector()
        # bot_connector.register_bot(self)
        # logger.info("Bot instance registered with BotConnector in setup_hook.")

async def main():
    """Main entry point for the bot"""
    try:
        # Set up intents
        intents = nextcord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        # Create the bot
        bot = HomelabBot(command_prefix="!", intents=intents)
        
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
