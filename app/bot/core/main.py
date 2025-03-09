# @/app/bot/core/main.py
import os
import nextcord
import sys
import asyncio
from nextcord.ext import commands
from infrastructure.config import EnvConfig, ServiceConfig, TaskConfig, ChannelConfig, DashboardConfig, ModuleServicesConfig
from infrastructure.logging import logger
from infrastructure.factories import BotComponentFactory, ServiceFactory, TaskFactory, DashboardFactory
from core.lifecycle.lifecycle_manager import BotLifecycleManager
from infrastructure.database.migrations.init_db import init_db
from infrastructure.managers.dashboard_manager import DashboardManager
from infrastructure.config.command_config import CommandConfig

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
    # Initialize database first
    await init_db()

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
        await initialize_bot()
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

if __name__ == '__main__':
    try:
        bot.run(env_config.discord_token)
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        sys.exit(1)
