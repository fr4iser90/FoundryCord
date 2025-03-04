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
from modules.security.encryption_commands import setup as setup_security
from modules.maintenance.cleanup_commands import setup as setup_cleanup_commands

from core.database.migrations.init_db import init_db
from core.utilities.logger import logger
import sys
import asyncio

# Intents für den Bot
intents = nextcord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
intents.dm_messages = True
intents.dm_reactions = True

# Bot initialisieren
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Bot ist online als {bot.user.name}")
    logger.info(f"Bot-ID: {bot.user.id}")
    logger.info(f"Slash-Commands sind aktiviert")
    logger.info(f"Verbunden mit {len(bot.guilds)} Servern")


# Set up general bot functionalities
setup_tasks(bot)

# Set up Middleware (Auth und Logging)
setup_middleware(bot)

setup_system_monitoring(bot)  # Monitoring setup
setup_cleanup_commands(bot)
setup_ip_management(bot)  # IP Whitelisting setup
setup_wireguard(bot)
setup_security(bot)
setup_project_tracker(bot)

# Bot starten
if __name__ == '__main__':
    # Initialize the database before starting the bot
    loop = asyncio.get_event_loop()
    try:
        if not loop.run_until_complete(init_db()):
            logger.error("Could not initialize database. Exiting.")
            sys.exit(1)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)
    
    # Start the bot
    bot.run(os.getenv('DISCORD_TOKEN'))
