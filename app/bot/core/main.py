# @/app/bot/core/main.py
import os
import nextcord
from nextcord.ext import commands
from core.startup import setup_bot
from modules.monitoring.system_monitoring import setup as setup_system_monitoring
# from modules.docker.container_management import setup as setup_container_management
from modules.tracker.ip_management import setup as setup_ip_management
from modules.middleware.auth_middleware import setup as setup_auth_middleware
from modules.middleware.logging_middleware import setup as setup_logging_middleware


# Intents für den Bot
intents = nextcord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True 

# Bot initialisieren
bot = commands.Bot(command_prefix='!', intents=intents)

# Set up general bot functionalities
setup_bot(bot)

# Set up Middleware (Auth und Logging)
setup_auth_middleware(bot)
setup_logging_middleware(bot)

setup_system_monitoring(bot)  # Monitoring setup
# setup_container_management(bot)  # Docker container management setup
setup_ip_management(bot)  # IP Whitelisting setup

# Bot starten
if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))

