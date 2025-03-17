# @/app/bot/core/main.py
import os
import logging
import asyncio
import nextcord
from nextcord.ext import commands
from typing import Dict, List, Any, Optional
from app.bot.core.shutdown_handler import ShutdownHandler
from app.bot.core.lifecycle.lifecycle_manager import LifecycleManager
from app.bot.core.workflow_manager import WorkflowManager
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.bot.core.workflows.category_workflow import CategoryWorkflow
from app.bot.core.workflows.channel_workflow import ChannelWorkflow
from app.bot.core.workflows.dashboard_workflow import DashboardWorkflow
from app.bot.core.workflows.task_workflow import TaskWorkflow
from app.bot.core.workflows.slash_commands_workflow import SlashCommandsWorkflow
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.config.env_config import EnvConfig

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
        
        # Load environment configuration
        self.env_config = EnvConfig().load()
        
        # Initialize lifecycle manager
        self.lifecycle = LifecycleManager()
        
        # Initialize workflow manager
        self.workflow_manager = WorkflowManager()
        
        # Create all workflow instances
        self.database_workflow = DatabaseWorkflow(self)
        self.category_workflow = CategoryWorkflow(self.database_workflow)
        self.channel_workflow = ChannelWorkflow(self.database_workflow, self.category_workflow)
        self.dashboard_workflow = DashboardWorkflow(self.database_workflow)
        self.task_workflow = TaskWorkflow(self)
        self.slash_commands_workflow = SlashCommandsWorkflow(self)
        
        # Register workflows with dependencies
        self.workflow_manager.register_workflow(self.database_workflow)
        self.workflow_manager.register_workflow(self.category_workflow, ['database'])
        self.workflow_manager.register_workflow(self.channel_workflow, ['database', 'category'])
        self.workflow_manager.register_workflow(self.dashboard_workflow, ['database'])
        self.workflow_manager.register_workflow(self.task_workflow, ['database'])
        self.workflow_manager.register_workflow(self.slash_commands_workflow, ['database'])
        
        # Set explicit initialization order
        self.workflow_manager.set_initialization_order([
            'database', 'category', 'channel', 'dashboard', 'task', 'slash_commands'
        ])
        
        # Add shutdown handler
        self.shutdown_handler = ShutdownHandler(self)
        
        # Store guild references
        self.guilds_by_id = {}
    
    async def on_ready(self):
        """Event triggered when the bot is ready"""
        logger.info(f"Logged in as {self.user.name}#{self.user.discriminator} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Store guild references for easy access
        for guild in self.guilds:
            self.guilds_by_id[guild.id] = guild
            logger.info(f"Connected to guild: {guild.name} (ID: {guild.id})")
        
        # Start initialization
        await self.start_initialization()
    
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
    
    async def sync_guild_data(self, guild: nextcord.Guild):
        """Synchronize database with Discord guild data"""
        logger.info(f"Syncing data for guild: {guild.name}")
        
        # Sync categories first
        await self.category_workflow.sync_with_discord(guild)
        
        # Then set them up (this will only create missing categories)
        categories = await self.category_workflow.setup_categories(guild)
        
        # Sync channels
        await self.channel_workflow.sync_with_discord(guild)
        
        # Set up channels
        channels = await self.channel_workflow.setup_channels(guild)
        
        logger.info(f"Finished syncing guild data for: {guild.name}")
        return {"categories": categories, "channels": channels}

    async def cleanup(self):
        """Clean up all resources before shutdown"""
        logger.info("Cleaning up bot resources")
        
        # Use the workflow manager to cleanup all workflows in reverse order
        await self.workflow_manager.cleanup_all()
        
        logger.info("Bot resources cleaned up successfully")

async def main():
    """
    Main entry point for the bot application.
    """
    try:
        # Configure bot with appropriate settings
        intents = nextcord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        # Create bot instance
        bot = HomelabBot(command_prefix="!", intents=intents)
        
        # Get token from environment variable
        token = os.environ.get("DISCORD_BOT_TOKEN")
        if not token:
            logger.error("DISCORD_BOT_TOKEN environment variable not set. Cannot start bot.")
            return

        # Start the bot
        logger.info("Starting the bot...")
        await bot.start(token)
        
    except Exception as e:
        logger.error(f"Fatal error in main bot process: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
