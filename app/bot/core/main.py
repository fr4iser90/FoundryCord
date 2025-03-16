# @/app/bot/core/main.py
import os
import nextcord
import sys
import asyncio
from nextcord.ext import commands
from app.bot.infrastructure.config import ServiceConfig, TaskConfig, ChannelConfig, CategoryConfig, DashboardConfig, ModuleServicesConfig
from app.shared.interface.logging.api import get_bot_logger, setup_bot_logging
from app.bot.infrastructure.factories import BotComponentFactory, ServiceFactory, TaskFactory, DashboardFactory
from app.bot.core.lifecycle.lifecycle_manager import BotLifecycleManager
from app.shared.infrastructure.database.migrations.init_db import init_db
from app.bot.infrastructure.managers.dashboard_manager import DashboardManager
from app.bot.infrastructure.config.command_config import CommandConfig
from app.shared.infrastructure.config.env_config import EnvConfig  # Import the shared EnvConfig


# Get a reference to the logger
logger = get_bot_logger()

# Load environment configuration
env_config = EnvConfig()
env_config.load()

# Initialize bot with environment settings
bot = commands.Bot(
    command_prefix='!!' if env_config.is_development else '!',
    intents=env_config.get_intents()
)

# Attach env_config to bot
bot.env_config = env_config

async def initialize_bot():
    # Initialize core components and factories first
    bot.lifecycle = BotLifecycleManager(bot)
    bot.factory = BotComponentFactory(bot)  # Main factory
    
    # IMPORTANT: Initialize dashboard manager and attach it to bot directly
    bot.dashboard_manager = await DashboardManager.setup(bot)
    
    # IMPORTANT: Set all factory references BEFORE registering configurations
    bot.component_factory = bot.factory     # For dashboards and UI components
    bot.service_factory = bot.factory.factories['service']  # For service creation
    bot.task_factory = bot.factory.factories['task']        # For task creation
    bot.dashboard_factory = bot.factory.factories['dashboard']  # For dashboard creation
    
    # NOW register configurations
    bot.category_config = CategoryConfig.register(bot)
    bot.channel_config = ChannelConfig.register(bot)
    bot.critical_services = ServiceConfig.register_critical_services(bot)
    bot.module_services = ModuleServicesConfig.register(bot)
    bot.tasks = TaskConfig.register_tasks(bot)
    bot.command_modules = CommandConfig.register_commands(bot)

    # Initialize through lifecycle manager
    await bot.lifecycle.initialize()

@bot.event
async def on_ready():
    try:
        # Just keep this - the service workflow will handle logging setup
        await initialize_bot()
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

# Add these two functions for entrypoint.py to use
def setup_bot():
    """Return the bot object for use by entrypoint.py"""
    return bot

async def run_bot_async(bot_instance):
    """Async version that entrypoint.py can use"""
    # This is just a placeholder for now - entrypoint will run the bot
    return bot_instance

# Original function - untouched
def run_bot():
    try:
        bot.run(env_config.DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    run_bot()
