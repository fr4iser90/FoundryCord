# @/app/bot/core/main.py
import os
import logging
import asyncio
import discord
from discord.ext import commands
from typing import Dict, List, Any, Optional
from app.bot.core.shutdown_handler import ShutdownHandler
from app.bot.core.lifecycle_manager import LifecycleManager
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.bot.core.workflows.category_workflow import CategoryWorkflow
from app.bot.core.workflows.channel_workflow import ChannelWorkflow
from app.bot.core.workflows.dashboard_workflow import DashboardWorkflow
from app.bot.core.workflows.task_workflow import TaskWorkflow
from app.bot.core.workflows.slash_commands_workflow import SlashCommandsWorkflow
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.config.env_config import EnvConfig

logger = get_bot_logger()

class HomelabBot(commands.Bot):
    """Main bot class for the Homelab Discord Bot"""
    
    def __init__(self, command_prefix="!", intents=None):
        if intents is None:
            intents = discord.Intents.default()
            intents.members = True
            intents.message_content = True
        
        super().__init__(command_prefix=command_prefix, intents=intents)
        
        # Load environment configuration
        self.env_config = EnvConfig().load()
        
        # Initialize lifecycle manager
        self.lifecycle = LifecycleManager()
        
        # Initialize workflows
        self.database_workflow = DatabaseWorkflow()
        self.category_workflow = CategoryWorkflow(self.database_workflow)
        self.channel_workflow = ChannelWorkflow(self.database_workflow, self.category_workflow)
        self.dashboard_workflow = None  # Will be initialized later
        self.task_workflow = None  # Will be initialized later
        self.slash_commands_workflow = None  # Will be initialized later
        
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
        
        try:
            # Initialize database
            if not await self.database_workflow.initialize():
                logger.error("Failed to initialize database")
                return False
            
            # Initialize config service (using the correct path)
            # Import the correct config service module
            from app.bot.application.services.config.config_service import ConfigService
            self.config_service = ConfigService(self)
            await self.config_service.initialize()
            
            # Initialize remaining components
            await self.category_workflow.initialize()
            await self.channel_workflow.initialize()
            
            # Initialize dashboard workflow after database is ready
            self.dashboard_workflow = DashboardWorkflow(self.database_workflow)
            await self.dashboard_workflow.initialize()
            
            # Initialize task workflow
            self.task_workflow = TaskWorkflow()
            await self.task_workflow.initialize(self)
            
            # Initialize slash commands workflow last
            self.slash_commands_workflow = SlashCommandsWorkflow(self)
            await self.slash_commands_workflow.initialize()
            
            logger.info("Bot initialization completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error during bot initialization: {e}")
            return False
    
    async def sync_guild_data(self, guild: discord.Guild):
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

async def main():
    """
    Main entry point for the bot application.
    """
    try:
        # Configure bot with appropriate settings
        intents = discord.Intents.default()
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
