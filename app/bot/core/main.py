# @/app/bot/core/main.py
import os
import nextcord
from nextcord.ext import commands
from core.tasks import setup_tasks
from modules.monitoring.system_monitoring import setup as setup_system_monitoring
from modules.tracker.ip_management import setup as setup_ip_management
from modules.tracker.project_tracker import setup as setup_project_tracker  
from core.middleware import setup as setup_middleware 
from modules.wireguard import setup as setup_wireguard
from modules.security import setup as setup_security
from modules.maintenance.cleanup_commands import setup as setup_cleanup_commands
from core.services.encryption import setup as setup_encryption
from core.services.auth import setup as setup_auth
from core.database.migrations.init_db import init_db
from core.services.logging import setup as setup_logging
from core.services.logging import logger
import sys
import asyncio
from core.startup import BotStartup
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment Configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production').lower()
IS_DEVELOPMENT = ENVIRONMENT == 'development'
IS_PRODUCTION = ENVIRONMENT == 'production'
IS_TESTING = ENVIRONMENT == 'testing'

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

# Initialize bot and startup
bot = commands.Bot(
    command_prefix='!!' if IS_DEVELOPMENT else '!', 
    intents=intents
)
bot.startup = BotStartup(bot)
bot.environment = ENVIRONMENT  # Store environment for use throughout the app

# Register critical services FIRST
bot.startup.register_service("Logging", setup_logging)
bot.startup.register_service("Auth", setup_auth)
bot.startup.register_service("Database", init_db)
bot.startup.register_service("Encryption", setup_encryption)

# Register module services
bot.startup.register_service("System Monitoring", setup_system_monitoring)
bot.startup.register_service("IP Management", setup_ip_management)
bot.startup.register_service("Wireguard", setup_wireguard)
bot.startup.register_service("Project Tracker", setup_project_tracker)

# Register middleware last as it depends on other services
bot.startup.register_service("Middleware", setup_middleware)

# Register tasks
from tasks.system_status import system_status_task
from tasks.cleanup_task import cleanup_task
from tasks.cleanup_dm_task import cleanup_dm_task
from tasks.project_tracker_task import project_tracker_task

bot.startup.register_task("System Status", system_status_task, HOMELAB_CHANNEL_ID)
bot.startup.register_task("Cleanup", cleanup_task, HOMELAB_CHANNEL_ID)
bot.startup.register_task("DM Cleanup", cleanup_dm_task)
bot.startup.register_task("Project Tracker", project_tracker_task, HOMELAB_CHANNEL_ID)

# Development mode specific services
if IS_DEVELOPMENT:
    try:
        from modules.maintenance.reload_commands import setup as setup_reload_commands
        bot.startup.register_service("Reload Commands", setup_reload_commands)
        logger.info(f"🔧 Running in {ENVIRONMENT.upper()} mode - Reload commands registered")
        
        # Development-specific features
        bot.dev_mode = True
    except ImportError as e:
        logger.warning(f"Failed to load development modules: {e}")

@bot.event
async def on_ready():
    try:
        if IS_DEVELOPMENT:
            logger.info(f"🔧 Running in {ENVIRONMENT.upper()} mode")
            await bot.change_presence(activity=nextcord.Game(name=f"🔧 {ENVIRONMENT.upper()}"))
        
        logger.info("Starting service initialization...")
        await bot.startup.initialize_services()
        logger.info("Service initialization complete")
        
        # Use the sync_commands method with timeout
        await bot.startup.sync_commands(timeout=60)
        
        # Start tasks regardless of sync result
        await bot.startup.start_tasks()
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
