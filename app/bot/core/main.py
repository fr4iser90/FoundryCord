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
bot = commands.Bot(command_prefix='!', intents=intents)
bot.startup = BotStartup(bot)

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

@bot.event
async def on_ready():
    try:
        logger.info("Starting service initialization...")
        await bot.startup.initialize_services()
        logger.info("Service initialization complete")
        
        # Simple command sync
        logger.info("Starting command synchronization...")
        start_time = time.time()
        await bot.sync_all_application_commands()
        sync_time = time.time() - start_time
        logger.info(f"Slash commands synced in {sync_time:.2f} seconds")
        
        # Start tasks
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
