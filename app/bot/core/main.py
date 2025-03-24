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
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.bot.core.workflows.category_workflow import CategoryWorkflow
from app.bot.core.workflows.channel_workflow import ChannelWorkflow
from app.bot.core.workflows.dashboard_workflow import DashboardWorkflow
from app.bot.core.workflows.task_workflow import TaskWorkflow
from app.shared.infrastructure.config.env_config import EnvConfig
from app.shared.domain.repositories.discord import GuildConfigRepository
from app.shared.infrastructure.database.session import session_context

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
        self.lifecycle = BotLifecycleManager()
        
        # Initialize workflow manager
        self.workflow_manager = BotWorkflowManager()
        
        # Create all workflow instances
        self.database_workflow = DatabaseWorkflow(self)
        self.category_workflow = CategoryWorkflow(self.database_workflow)
        self.channel_workflow = ChannelWorkflow(self.database_workflow, self.category_workflow)
        self.dashboard_workflow = DashboardWorkflow(self.database_workflow, bot=self)
        self.task_workflow = TaskWorkflow(self)
        #self.slash_commands_workflow = SlashCommandsWorkflow(self)
        
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
        """Called when the bot is ready"""
        logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")
        
        # Store guild references for quick access
        self.guilds_by_id = {}
        for guild in self.guilds:
            self.guilds_by_id[guild.id] = guild
            logger.info(f"Connected to guild: {guild.name} (ID: {guild.id})")
            
            # Create default configuration for new guilds
            async with session_context() as session:
                guild_config_repo = GuildConfigRepository(session)
                existing_config = await guild_config_repo.get_by_guild_id(str(guild.id))
                
                if not existing_config:
                    logger.info(f"Creating default configuration for guild: {guild.name}")
                    await guild_config_repo.create_or_update(
                        guild_id=str(guild.id),
                        guild_name=guild.name
                    )
        
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
        
        # Get guild configuration
        async with session_context() as session:
            guild_config_repo = GuildConfigRepository(session)
            config = await guild_config_repo.get_by_guild_id(str(guild.id))
            
            if not config:
                logger.warning(f"No configuration found for guild {guild.name}, using defaults")
                # Create default configuration
                config = await guild_config_repo.create_or_update(
                    guild_id=str(guild.id),
                    guild_name=guild.name
                )
        
        # Only run workflows that are enabled for this guild
        results = {}
        
        # Sync categories if enabled
        if config.enable_categories:
            # Sync categories first
            await self.category_workflow.sync_with_discord(guild)
            
            # Then set them up (this will only create missing categories)
            categories = await self.category_workflow.setup_categories(guild)
            results["categories"] = categories
        
        # Sync channels if enabled
        if config.enable_channels:
            # Sync channels
            await self.channel_workflow.sync_with_discord(guild)
            
            # Set up channels
            channels = await self.channel_workflow.setup_channels(guild)
            results["channels"] = channels
        
        # Sync dashboard if enabled
        if config.enable_dashboard and hasattr(self, 'dashboard_workflow'):
            # Set up dashboard
            dashboard = await self.dashboard_workflow.setup_guild_dashboard(guild)
            results["dashboard"] = dashboard
        
        logger.info(f"Finished syncing guild data for: {guild.name}")
        return results

    async def cleanup(self):
        """Clean up all resources before shutdown"""
        logger.info("Cleaning up bot resources")
        
        # Use the workflow manager to cleanup all workflows in reverse order
        await self.workflow_manager.cleanup_all()
        
        logger.info("Bot resources cleaned up successfully")

    async def setup_hook(self):
        """Setup hook that runs before the bot starts"""
        from app.bot.domain.services.bot_control_service import BotControlService
        self.control_service = BotControlService(self)
        
        # Register the bot with the connector for web interface
        from app.shared.infrastructure.integration.bot_connector import BotConnector
        bot_connector = BotConnector()
        bot_connector.register_bot(self)
        
async def main():
    """Main entry point for the bot"""
    try:
        # Lade Umgebungsvariablen mit EnvConfig
        env_config = EnvConfig().load()
        
        # Set up intents
        intents = env_config.get_intents()
        
        # Create the bot
        bot = commands.Bot(command_prefix="!", intents=intents)
        
        # Set up shutdown handler
        shutdown_handler = ShutdownHandler(bot)
        
        # Initialize workflow manager
        workflow_manager = BotWorkflowManager()
        
        # Register workflows
        database_workflow = DatabaseWorkflow(bot)
        workflow_manager.register_workflow(database_workflow)
        
        category_workflow = CategoryWorkflow(database_workflow)
        workflow_manager.register_workflow(category_workflow)
        
        channel_workflow = ChannelWorkflow(category_workflow, database_workflow)
        workflow_manager.register_workflow(channel_workflow)
        
        # Wichtig: Hier den Bot-Parameter übergeben
        dashboard_workflow = DashboardWorkflow(database_workflow, bot=bot)
        workflow_manager.register_workflow(dashboard_workflow)
        
        task_workflow = TaskWorkflow(bot)
        workflow_manager.register_workflow(task_workflow)
        
        # Set initialization order
        workflow_manager.set_initialization_order([
            "database",
            "category",
            "channel",
            "dashboard",
            "task",
            "slash_commands"  # This might not be registered yet
        ])
        
        # Store workflow manager on bot for access
        bot.workflow_manager = workflow_manager
        
        # Add cleanup method to bot
        bot.cleanup = workflow_manager.cleanup_all
        
        @bot.event
        async def on_ready():
            """Called when the bot is ready"""
            logger.info(f"Logged in as {bot.user.name}#{bot.user.discriminator} (ID: {bot.user.id})")
            
            # Log connected guilds
            guilds = bot.guilds
            logger.info(f"Connected to {len(guilds)} guilds")
            for guild in guilds:
                logger.info(f"Connected to guild: {guild.name} (ID: {guild.id})")
            
            # Initialize workflows
            logger.info("Starting bot initialization")
            try:
                logger.info("Initializing all workflows")
                if await workflow_manager.initialize_all():
                    logger.info("All workflows initialized successfully")
                    
                    # Set up categories and channels for each guild
                    for guild in bot.guilds:
                        # Get category workflow
                        category_wf = workflow_manager.get_workflow("category")
                        if category_wf:
                            # Set up categories
                            categories = await category_wf.setup_categories(guild)
                            logger.info(f"Set up {len(categories)} categories for guild {guild.name}")
                            
                            # Sync with Discord
                            await category_wf.sync_with_discord(guild)
                            
                        # Get channel workflow
                        channel_wf = workflow_manager.get_workflow("channel")
                        if channel_wf:
                            # Set up channels
                            channels = await channel_wf.setup_channels(guild)
                            logger.info(f"Set up {len(channels)} channels for guild {guild.name}")
                            
                            # Sync with Discord
                            await channel_wf.sync_with_discord(guild)
                else:
                    logger.error("Bot initialization failed")
            except Exception as e:
                logger.error(f"Error during bot initialization: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Run the bot
        logger.info("Starting the bot...")
        
        # Start the bot mit dem Token aus env_config
        await bot.start(env_config.DISCORD_BOT_TOKEN)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
