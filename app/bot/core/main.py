# @/app/bot/core/main.py
import os
import logging
import asyncio
import discord
from discord.ext import commands
from typing import Dict, List, Any, Optional
from app.bot.core.shutdown_handler import ShutdownHandler
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.bot.core.workflows.category_workflow import CategoryWorkflow
from app.bot.core.workflows.channel_workflow import ChannelWorkflow
from app.bot.core.workflows.dashboard_workflow import DashboardWorkflow
from app.bot.core.workflows.task_workflow import TaskWorkflow
from app.bot.core.workflows.slash_commands_workflow import SlashCommandsWorkflow
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class HomelabBot(commands.Bot):
    """Main bot class for the Homelab Discord Bot"""
    
    def __init__(self, command_prefix="!", intents=None):
        if intents is None:
            intents = discord.Intents.default()
            intents.members = True
            intents.message_content = True
        
        super().__init__(command_prefix=command_prefix, intents=intents)
        
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
        """Initialize the bot components"""
        logger.info("Starting bot initialization...")
        
        # Initialize database
        logger.info("Initializing database connections...")
        await self.database_workflow.initialize()
        
        # Initialize services
        logger.info("Initializing services...")
        logger.info("Creating config service")
        # TODO: Add config service initialization
        
        logger.info("Creating event service")
        # TODO: Add event service initialization
        
        # Initialize workflows
        logger.info("Initializing workflows...")
        
        # Initialize category workflow
        await self.category_workflow.initialize()
        
        # Initialize channel workflow
        logger.info("Creating channel workflow")
        logger.info("Initializing channel workflow")
        await self.channel_workflow.initialize()
        
        # Initialize dashboard workflow
        logger.info("Creating dashboard workflow with domain model integration")
        self.dashboard_workflow = DashboardWorkflow(self)
        logger.info("Initializing dashboard workflow with domain model")
        await self.dashboard_workflow.initialize()
        
        # Initialize command workflow
        logger.info("Creating command workflow")
        self.slash_commands_workflow = SlashCommandsWorkflow(self)
        logger.info("Initializing command workflow")
        await self.slash_commands_workflow.initialize()
        
        # Initialize task workflow
        logger.info("Creating task workflow")
        self.task_workflow = TaskWorkflow(self)
        logger.info("Initializing task workflow")
        await self.task_workflow.initialize()
        
        # Start background tasks
        logger.info("Starting background tasks...")
        
        # Start dashboard background tasks
        logger.info("Starting dashboard background tasks")
        self.dashboard_workflow.start_background_tasks()
        
        # Start task background tasks
        logger.info("Starting task background tasks")
        self.task_workflow.start_background_tasks()
        
        # Sync channels and categories for each guild
        for guild in self.guilds:
            await self.sync_guild_data(guild)
        
        logger.info("Initialization sequence completed")
    
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

async def start_bot():
    """Start the bot"""
    # Create bot instance
    bot = HomelabBot()
    
    # Start the bot
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("No Discord token provided. Please set the DISCORD_TOKEN environment variable.")
        return
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
    finally:
        await bot.close()

def run_bot():
    """Run the bot"""
    logger.info("Starting bot...")
    asyncio.run(start_bot())

if __name__ == "__main__":
    run_bot()
