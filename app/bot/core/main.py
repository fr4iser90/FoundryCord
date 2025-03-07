# @/app/bot/core/main.py
import os
import nextcord
import sys
import asyncio
from nextcord.ext import commands
from modules.monitoring.system_monitoring import setup as setup_system_monitoring
from modules.tracker.ip_management import setup as setup_ip_management
from modules.tracker.project_tracker import setup as setup_project_tracker  
from modules.wireguard import setup as setup_wireguard
from modules.security import setup as setup_security
from modules.maintenance.cleanup_commands import setup as setup_cleanup_commands
from infrastructure.encryption import setup as setup_encryption
from services.auth import setup as setup_auth
from infrastructure.database.migrations.init_db import init_db
from infrastructure.logging import setup as setup_logging
from infrastructure.logging import logger
from infrastructure.rate_limiting import setup as setup_rate_limiting
from infrastructure.factories import BotComponentFactory, ServiceFactory, TaskFactory
from core.lifecycle.lifecycle_manager import BotLifecycleManager
from infrastructure.discord.command_sync_service import CommandSyncService
# Add command imports after services
from interfaces.commands.auth import setup as setup_auth_commands

import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment Configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production').lower()
IS_DEVELOPMENT = ENVIRONMENT == 'development'
IS_PRODUCTION = ENVIRONMENT == 'production'
IS_TESTING = ENVIRONMENT == 'testing'

# Environment Configuration
GUILD_ID = int(os.getenv('DISCORD_SERVER'))
HOMELAB_CHANNEL_ID = int(os.getenv('DISCORD_HOMELAB_CHANNEL'))

# Intents für den Bot
intents = nextcord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
intents.dm_messages = True
intents.guild_messages = True
intents.dm_reactions = True

# Initialize bot and factory components
bot = commands.Bot(
    command_prefix='!!' if IS_DEVELOPMENT else '!', 
    intents=intents
)

# Initialize core components in correct order
bot.lifecycle = BotLifecycleManager(bot)  # Lifecycle FIRST
bot.service_factory = ServiceFactory(bot)  # Then factories
bot.task_factory = TaskFactory(bot)
bot.factory = BotComponentFactory(bot)

# Create services using specialized factory
critical_services = [
    bot.service_factory.create("Logging", setup_logging),
    bot.service_factory.create("Auth", setup_auth),
    bot.service_factory.create("Database", init_db),
    bot.service_factory.create("Encryption", setup_encryption),
    bot.service_factory.create("RateLimiting", setup_rate_limiting)  # Add this line
]

# Register module services
module_services = [
    bot.factory.create_service("System Monitoring", setup_system_monitoring),
    bot.factory.create_service("IP Management", setup_ip_management),
    bot.factory.create_service("Wireguard", setup_wireguard),
    bot.factory.create_service("Project Tracker", setup_project_tracker),
]

# Register tasks
from tasks.system_status import system_status_task
from tasks.cleanup_task import cleanup_task
from tasks.cleanup_dm_task import cleanup_dm_task
from tasks.project_tracker_task import project_tracker_task

# Create tasks using specialized factory
tasks = [
    bot.task_factory.create("System Status", system_status_task, HOMELAB_CHANNEL_ID),
    bot.task_factory.create("Cleanup", cleanup_task, HOMELAB_CHANNEL_ID),
    bot.task_factory.create("DM Cleanup", cleanup_dm_task),
    bot.task_factory.create("Project Tracker", project_tracker_task, HOMELAB_CHANNEL_ID)
]

# Development mode specific services
if IS_DEVELOPMENT:
    try:
        from dev.reload_commands import setup as setup_reload_commands
        dev_services = [
            bot.factory.create_service("Reload Commands", setup_reload_commands)
        ]
        logger.info(f"🔧 Running in {ENVIRONMENT.upper()} mode - Reload commands registered")
        
        # Development-specific features
        bot.dev_mode = True
    except ImportError as e:
        logger.warning(f"Failed to load development modules: {e}")
        dev_services = []
else:
    dev_services = []

@bot.event
async def on_ready():
    try:
        if IS_DEVELOPMENT:
            logger.info(f"🔧 Running in {ENVIRONMENT.upper()} mode")
            await bot.change_presence(activity=nextcord.Game(name=f"🔧 {ENVIRONMENT.upper()}"))
        
        # Initialize command sync service
        await bot.lifecycle.setup_command_sync(
            enable_guild_sync=True,
            enable_global_sync=True,
            timeout=180
        )
        
        # Initialize critical services first
        logger.info("Starting critical service initialization...")
        for service in critical_services:
            if not hasattr(bot, 'lifecycle'):
                logger.error("Lifecycle manager not initialized!")
                raise RuntimeError("Lifecycle manager must be initialized before services")
            await bot.lifecycle.add_service(service)
        
        # Initialize module services
        logger.info("Starting module service initialization...")
        for service in module_services:
            await bot.lifecycle.add_service(service)
            
        # Initialize development services if any
        if dev_services:
            logger.info("Starting development service initialization...")
            for service in dev_services:
                await bot.lifecycle.add_service(service)
        
        # Initialize auth commands explicitly
        auth_commands_service = bot.factory.create_service("Auth Commands", setup_auth_commands)
        await bot.lifecycle.add_service(auth_commands_service)
        
        # Sync commands in background instead of blocking
        logger.info("Starting command synchronization in background...")
        await bot.lifecycle.command_sync_service.start_background_sync()
        
        # Start tasks
        logger.info("Starting background tasks...")
        for task in tasks:
            await bot.lifecycle.add_task(task)
            
        logger.info("Startup sequence complete")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        bot.run(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        sys.exit(1)
