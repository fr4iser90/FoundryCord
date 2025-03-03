# @/app/bot/core/main.py
import os
import nextcord
from nextcord.ext import commands
from core.tasks import setup_tasks
from modules.monitoring.system_monitoring import setup as setup_system_monitoring
from modules.tracker.ip_management import setup as setup_ip_management
from core.middleware import setup as setup_middleware 
from modules.wireguard import setup as setup_wireguard
from modules.security.encryption_commands import setup as setup_security
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

# Set up general bot functionalities
setup_tasks(bot)

# Set up Middleware (Auth und Logging)
setup_middleware(bot)

setup_system_monitoring(bot)  # Monitoring setup
# setup_container_management(bot)  # Docker container management setup
setup_ip_management(bot)  # IP Whitelisting setup
setup_wireguard(bot)
setup_security(bot)

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
