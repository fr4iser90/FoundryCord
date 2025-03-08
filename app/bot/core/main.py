# @/app/bot/core/main.py
import os
import nextcord
import sys
import asyncio
from nextcord.ext import commands
from infrastructure.config import EnvConfig, ServiceConfig, TaskConfig, ChannelConfig, DashboardConfig
from infrastructure.logging import logger
from infrastructure.factories import BotComponentFactory, ServiceFactory, TaskFactory, DashboardFactory
from core.lifecycle.lifecycle_manager import BotLifecycleManager
from infrastructure.database.migrations.init_db import init_db

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

    # Initialize core components
    bot.lifecycle = BotLifecycleManager(bot)
    bot.service_factory = ServiceFactory(bot)
    bot.task_factory = TaskFactory(bot)
    bot.dashboard_factory = DashboardFactory(bot)
    bot.factory = BotComponentFactory(bot)

    # Load configurations AFTER database is initialized
    critical_services = ServiceConfig.register_critical_services(bot)
    module_services = ServiceConfig.register_module_services(bot)
    tasks = TaskConfig.register_tasks(bot)
    channel_setup = ChannelConfig.register(bot)
    dashboards = DashboardConfig.register(bot)

    return critical_services, module_services, tasks, channel_setup, dashboards

@bot.event
async def on_ready():
    try:
        critical_services, module_services, tasks, channel_setup, dashboards = await initialize_bot()
        await bot.lifecycle.initialize(
            critical_services=critical_services,
            channel_setup=channel_setup,
            dashboards=dashboards,
            module_services=module_services,
            tasks=tasks,
        )
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

if __name__ == '__main__':
    try:
        bot.run(env_config.discord_token)
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        sys.exit(1)
